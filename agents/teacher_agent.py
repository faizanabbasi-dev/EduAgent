





from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
#from langchain.callbacks.tracers import LangChainTracer
from rag.retriever import retrieve_relevant_docs, format_context
from config.settings import settings
from typing import List, Dict

def get_llm():
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.7,
        max_tokens=1024
    )

TEACHER_SYSTEM_PROMPT = """You are EduAgent — an expert AI teacher and learning assistant.

Your role:
- Explain concepts clearly with examples
- Use the provided document context when available
- Break complex topics into simple steps
- Encourage the student and track their understanding
- Always ask a follow-up question to check comprehension

When context is provided, base your answer on it. 
When no context is available, use your general knowledge.
Keep responses concise but complete. Use bullet points for clarity."""

def teach(
    user_message: str,
    chat_history: List[Dict] = None,
    use_rag: bool = True
) -> Dict:
    """
    Teacher agent: answers questions with optional RAG context
    Returns: {response, sources, used_rag}
    """
    llm = get_llm()
    
    # RAG: retrieve relevant docs
    context = ""
    sources = []
    if use_rag:
        docs = retrieve_relevant_docs(user_message, k=4)
        if docs:
            context = format_context(docs)
            sources = [d.metadata.get("source", "") for d in docs]
    
    # Build messages
    messages = [SystemMessage(content=TEACHER_SYSTEM_PROMPT)]
    
    # Add context if available
    if context and context != "No relevant documents found.":
        context_msg = f"RELEVANT CONTEXT FROM DOCUMENTS:\n{context}\n\nUse this context to answer the student's question."
        messages.append(HumanMessage(content=context_msg))
        messages.append(AIMessage(content="Understood. I'll use this context to provide an accurate answer."))
    
    # Add chat history
    if chat_history:
        for msg in chat_history[-6:]:  # last 3 turns
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
    
    # Add current question
    messages.append(HumanMessage(content=user_message))
    
    response = llm.invoke(messages)
    
    return {
        "response": response.content,
        "sources": list(set(sources)),
        "used_rag": bool(sources)
    }
