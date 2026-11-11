from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ChatRequest(BaseModel):
    user_id: str = "default_user"
    session_id: Optional[str] = None
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    session_id: str
    response: str
    type: str
    sources: List[str] = []
    used_rag: bool = False

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5

class QuizSubmitRequest(BaseModel):
    topic: str
    user_id: str = "default_user"
    questions: List[Dict]
    answers: Dict[str, str]

class ResearchRequest(BaseModel):
    topic: str

class UploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_added: int
    message: str

class ProgressResponse(BaseModel):
    user_id: str
    topics: List[Dict[str, Any]]
    total_questions: int
    average_score: float
