# 🎓 EduAgent — AI Learning Assistant
**Multi-Agent Education System | Phase 3-5 Roadmap Project**

## Stack
| Component | Technology |
|-----------|-----------|
| LLM | Groq Llama3-70b (Free) |
| Agent Framework | LangChain + LangGraph |
| Multi-Agent | Phase 5 via LangGraph StateGraph |
| RAG | ChromaDB + HuggingFace Embeddings |
| Backend | FastAPI |
| Database | SQLite + SQLAlchemy |
| Monitoring | LangSmith (optional) |

## Features
- 💬 **Chat** — Ask anything, auto-routes to right agent
- 📝 **Quiz** — Generate + evaluate MCQ quizzes on any topic
- 🔬 **Research** — Get structured study plans
- 📤 **Upload** — Add PDFs/TXTs to knowledge base (RAG)
- 📊 **Progress** — Track quiz scores and learning history

## Setup (Windows)

### 1. Clone / Download project
```bash
cd eduagent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment
```bash
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
# Get free key from: https://console.groq.com
```

### 5. Run
```bash
python run.py
```

### 6. Open browser
```
http://localhost:8000
```

## API Docs
```
http://localhost:8000/docs
```

## Agents
- **Teacher Agent** — Explains concepts with RAG context
- **Researcher Agent** — Creates study plans
- **Evaluator Agent** — Generates and evaluates quizzes
- **Orchestrator** — LangGraph StateGraph routing all agents

## Portfolio Value
This project demonstrates:
- ✅ RAG Pipeline (Phase 3)
- ✅ FastAPI Deployment (Phase 3)
- ✅ Multi-Agent with LangGraph (Phase 5)
- ✅ Vector DB (ChromaDB) (Phase 3)
- ✅ LangSmith Monitoring ready (Phase 5)
