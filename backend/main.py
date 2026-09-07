from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import knowledge, analyze, predict, chat, history

app = FastAPI(
    title="Intelligent Bug Diagnosis Platform",
    description="Multi-agent platform for bug diagnosis and fix recommendation",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(knowledge.router)
app.include_router(analyze.router)
app.include_router(predict.router)
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/")
def root():
    return {"status": "running", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    import json
    from config import SEED_DATA_PATH, GEMINI_API_KEY
    with open(SEED_DATA_PATH) as f:
        count = len(json.load(f))
    return {"status": "healthy", "bugs_in_kb": count, "gemini_configured": bool(GEMINI_API_KEY)}
