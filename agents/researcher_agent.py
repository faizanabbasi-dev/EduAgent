





from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from rag.retriever import retrieve_relevant_docs, format_context
from config.settings import settings
import json, re

def get_llm():
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.2,
        max_tokens=1500
    )

RESEARCHER_SYSTEM_PROMPT = """You are a research assistant that creates detailed study plans and summaries.
When given a topic and documents, you:
1. Identify key concepts
2. Create a structured learning path
3. Summarize main points
4. Suggest what to study first

Respond ONLY with valid JSON. No extra text.

Format:
{
  "topic": "topic name",
  "summary": "2-3 sentence overview",
  "key_concepts": ["concept1", "concept2", "concept3"],
  "learning_path": [
    {"step": 1, "title": "Start here", "description": "What to do"},
    {"step": 2, "title": "Next", "description": "What to do next"}
  ],
  "estimated_time": "X hours",
  "difficulty": "Beginner/Intermediate/Advanced"
}"""

def research_topic(topic: str) -> dict:
    """Research a topic and create a study plan"""
    llm = get_llm()
    
    # Get relevant docs
    docs = retrieve_relevant_docs(topic, k=6)
    context = format_context(docs)
    
    content = f"Create a study plan for: {topic}"
    if context != "No relevant documents found.":
        content += f"\n\nAvailable content:\n{context[:2000]}"
    
    messages = [
        SystemMessage(content=RESEARCHER_SYSTEM_PROMPT),
        HumanMessage(content=content)
    ]
    
    response = llm.invoke(messages)
    
    try:
        text = response.content.strip()
        text = re.sub(r'```json\s*|\s*```', '', text)
        data = json.loads(text)
        return {"success": True, "data": data}
    except json.JSONDecodeError:
        # Fallback: return raw
        return {
            "success": True,
            "data": {
                "topic": topic,
                "summary": response.content,
                "key_concepts": [],
                "learning_path": [],
                "estimated_time": "Unknown",
                "difficulty": "Unknown"
            }
        }
