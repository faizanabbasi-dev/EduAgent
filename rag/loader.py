





import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings

def load_document(file_path: str) -> list:
    """Load PDF or TXT document and split into chunks"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"✅ Loaded {len(chunks)} chunks from {os.path.basename(file_path)}")
    return chunks

def save_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file to docs_store"""
    os.makedirs(settings.DOCS_STORE_PATH, exist_ok=True)
    file_path = os.path.join(settings.DOCS_STORE_PATH, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path
