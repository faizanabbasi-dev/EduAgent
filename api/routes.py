from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User, ChatSession, Message, UserProgress, Document
from api.schemas import *
from agents.orchestrator import run_agent
from agents.teacher_agent import teach
from agents.evaluator_agent import generate_quiz, evaluate_answers
from agents.researcher_agent import research_topic
from rag.loader import load_document, save_uploaded_file
from rag.embeddings import add_documents_to_store
from datetime import datetime
import uuid, os

router = APIRouter()

# ---------- Helper ----------
def get_or_create_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        user = User(username=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# ---------- Chat ----------
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint — routes to appropriate agent automatically"""
    user = get_or_create_user(db, request.user_id)
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(
            user_id=user.id,
            session_id=session_id,
            topic=request.message[:100]
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get history
    history_msgs = db.query(Message).filter(
        Message.session_id == session.id
    ).order_by(Message.timestamp.desc()).limit(10).all()
    
    chat_history = [
        {"role": m.role, "content": m.content}
        for m in reversed(history_msgs)
    ]
    
    # Run agent
    result = run_agent(request.message, chat_history)
    
    # Get response text
    if result["type"] == "teaching":
        response_text = result["content"]
        sources = result.get("sources", [])
        used_rag = result.get("used_rag", False)
    elif result["type"] == "research":
        data = result["content"].get("data", {})
        response_text = f"📚 Study Plan: {data.get('topic', '')}\n\n{data.get('summary', '')}"
        sources = []
        used_rag = False
    elif result["type"] == "quiz":
        response_text = "Quiz generated! Check /quiz endpoint for structured quiz."
        sources = []
        used_rag = False
    else:
        response_text = "I couldn't process that request. Please try again."
        sources = []
        used_rag = False
    
    # Save to DB
    db.add(Message(session_id=session.id, role="user", content=request.message))
    db.add(Message(session_id=session.id, role="assistant", content=response_text))
    db.commit()
    
    return ChatResponse(
        session_id=session_id,
        response=response_text,
        type=result["type"],
        sources=sources,
        used_rag=used_rag
    )

# ---------- Quiz ----------
@router.post("/quiz/generate")
async def generate_quiz_endpoint(request: QuizRequest):
    """Generate a quiz on any topic"""
    result = generate_quiz(request.topic, request.num_questions)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result["data"]

@router.post("/quiz/submit")
async def submit_quiz(request: QuizSubmitRequest, db: Session = Depends(get_db)):
    """Submit quiz answers and get evaluation"""
    user = get_or_create_user(db, request.user_id)
    
    result = evaluate_answers(request.questions, request.answers)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    eval_data = result["data"]
    score_pct = eval_data.get("score", 0)
    
    # Update progress in DB
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.topic == request.topic
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=user.id, topic=request.topic)
        db.add(progress)
    
    progress.questions_attempted += len(request.questions)
    correct = int(len(request.questions) * score_pct / 100)
    progress.questions_correct += correct
    progress.quiz_score = score_pct
    progress.last_updated = datetime.utcnow()
    db.commit()
    
    return eval_data

# ---------- Research ----------
@router.post("/research")
async def research_endpoint(request: ResearchRequest):
    """Get study plan and summary for a topic"""
    result = research_topic(request.topic)
    if not result["success"]:
        raise HTTPException(status_code=500, detail="Research failed")
    return result["data"]

# ---------- Upload ----------
@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    topic: str = Form("general"),
    db: Session = Depends(get_db)
):
    """Upload PDF/TXT and add to RAG knowledge base"""
    allowed = [".pdf", ".txt", ".md"]
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type not supported. Use: {allowed}")
    
    file_bytes = await file.read()
    file_path = save_uploaded_file(file_bytes, file.filename)
    
    chunks = load_document(file_path)
    add_documents_to_store(chunks)
    
    # Save to DB
    doc = Document(
        filename=file.filename,
        file_path=file_path,
        topic=topic,
        chunk_count=len(chunks)
    )
    db.add(doc)
    db.commit()
    
    return UploadResponse(
        success=True,
        filename=file.filename,
        chunks_added=len(chunks),
        message=f"Successfully added {len(chunks)} chunks to knowledge base"
    )

# ---------- Progress ----------
@router.get("/progress/{user_id}")
async def get_progress(user_id: str, db: Session = Depends(get_db)):
    """Get user's learning progress"""
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        return {"user_id": user_id, "topics": [], "total_questions": 0, "average_score": 0}
    
    progress_list = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()
    
    topics = [
        {
            "topic": p.topic,
            "quiz_score": p.quiz_score,
            "questions_attempted": p.questions_attempted,
            "questions_correct": p.questions_correct,
            "last_updated": p.last_updated.isoformat()
        }
        for p in progress_list
    ]
    
    total_q = sum(p.questions_attempted for p in progress_list)
    avg_score = sum(p.quiz_score for p in progress_list) / len(progress_list) if progress_list else 0
    
    return {
        "user_id": user_id,
        "topics": topics,
        "total_questions": total_q,
        "average_score": round(avg_score, 2)
    }

# ---------- Documents ----------
@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    docs = db.query(Document).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "topic": d.topic,
            "chunks": d.chunk_count,
            "uploaded": d.uploaded_at.isoformat()
        }
        for d in docs
    ]

@router.get("/health")
async def health():
    return {"status": "ok", "agent": "EduAgent v1.0", "phase": "Phase 3-5"}
@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(doc)
    db.commit()
    return {"success": True}