from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router
from db.database import init_db
from config.settings import settings
import os

app = FastAPI(
    title="EduAgent - AI Learning Assistant",
    description="Multi-Agent Education System | Phase 3-5 | LangGraph + RAG + Groq",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    init_db()
    os.makedirs(settings.DOCS_STORE_PATH, exist_ok=True)
    os.makedirs(settings.CHROMA_PATH, exist_ok=True)
    print("EduAgent started!")
    print(f"Docs: http://localhost:{settings.APP_PORT}/docs")

@app.get("/")
async def root():
    return FileResponse("static/index.html")
