






from rag.embeddings import get_vectorstore
from langchain_core.documents import Document
from typing import List

def retrieve_relevant_docs(query: str, k: int = 4, collection_name: str = "eduagent_docs") -> List[Document]:
    """Retrieve top-k relevant chunks for a query"""
    try:
        vectorstore = get_vectorstore(collection_name)
        docs = vectorstore.similarity_search(query, k=k)
        return docs
    except Exception as e:
        print(f"⚠️ Retrieval error: {e}")
        return []

def format_context(docs: List[Document]) -> str:
    """Format retrieved docs into context string"""
    if not docs:
        return "No relevant documents found."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "")
        page_info = f" (Page {page})" if page else ""
        context_parts.append(f"[Source {i}{page_info}]: {doc.page_content}")
    
    return "\n\n".join(context_parts)
