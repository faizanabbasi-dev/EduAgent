
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
import json, re

def get_llm():
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.3,
        max_tokens=1024
    )

QUIZ_SYSTEM_PROMPT = """You are a quiz generator. Generate exactly the requested number of MCQ questions.
IMPORTANT: Respond ONLY with valid JSON. No extra text, no markdown, no backticks.

Format:
{
  "questions": [
    {
      "id": 1,
      "question": "Question text?",
      "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
      "correct_answer": "A",
      "explanation": "Brief explanation why A is correct"
    }
  ]
}"""

EVALUATE_SYSTEM_PROMPT = """You are an evaluator. Evaluate the student's answers and provide feedback.
Respond ONLY with valid JSON. No extra text.

Format:
{
  "score": 80,
  "total": 100,
  "feedback": "Overall feedback here",
  "results": [
    {
      "question_id": 1,
      "correct": true,
      "explanation": "explanation"
    }
  ]
}"""

def generate_quiz(topic: str, num_questions: int = 5, context: str = "") -> dict:
    llm = get_llm()
    content = f"Generate {num_questions} MCQ questions about: {topic}"
    if context:
        content += f"\n\nBase questions on this content:\n{context[:1500]}"
    messages = [
        SystemMessage(content=QUIZ_SYSTEM_PROMPT),
        HumanMessage(content=content)
    ]
    response = llm.invoke(messages)
    try:
        text = response.content.strip()
        text = re.sub(r'```json\s*|\s*```', '', text)
        quiz_data = json.loads(text)
        return {"success": True, "data": quiz_data}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse error: {e}", "raw": response.content}

def evaluate_answers(questions: list, user_answers: dict) -> dict:
    llm = get_llm()
    eval_data = []
    for q in questions:
        qid = str(q["id"])
        user_ans = user_answers.get(qid, user_answers.get(int(q["id"]), ""))
        eval_data.append({
            "id": q["id"],
            "question": q["question"],
            "correct_answer": q["correct_answer"],
            "user_answer": user_ans,
            "explanation": q.get("explanation", "")
        })
    messages = [
        SystemMessage(content=EVALUATE_SYSTEM_PROMPT),
        HumanMessage(content=f"Evaluate these answers:\n{json.dumps(eval_data, indent=2)}")
    ]
    response = llm.invoke(messages)
    try:
        text = response.content.strip()
        text = re.sub(r'```json\s*|\s*```', '', text)
        result = json.loads(text)
        return {"success": True, "data": result}
    except json.JSONDecodeError as e:
        return {"success": False, "error": str(e)}