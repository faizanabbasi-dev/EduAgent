import chromadb
from chromadb.utils import embedding_functions
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import settings
import os

def get_embeddings():
    """Use free HuggingFace embeddings - no API key needed"""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

def get_vectorstore(collection_name: str = "eduagent_docs"):
    """Get or create ChromaDB vectorstore"""
    os.makedirs(settings.CHROMA_PATH, exist_ok=True)
    embeddings = get_embeddings()
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH
    )
    return vectorstore

def add_documents_to_store(chunks: list, collection_name: str = "eduagent_docs"):
    """Add document chunks to ChromaDB"""
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(chunks)
    print(f"✅ Added {len(chunks)} chunks to ChromaDB")
    return vectorstore
