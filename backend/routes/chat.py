import json
from fastapi import APIRouter
from models.bug_report import ChatMessage
from agents import chat_agent
from config import SEED_DATA_PATH

router = APIRouter(prefix="/api", tags=["Chat"])

@router.post("/chat")
async def chat(msg: ChatMessage):
    context = ""
    source_ids = []
    try:
        with open(SEED_DATA_PATH, "r") as f:
            bugs = json.load(f)
        for bug in bugs[:3]:
            context += f"\nBug {bug['id']}: {bug['title']}\nRoot Cause: {bug.get('root_cause','')}\nResolution: {bug.get('resolution','')}\n---"
            source_ids.append(bug["id"])
    except Exception as e:
        print(f"KB load failed: {e}")
    try:
        result = await chat_agent.run({"message": msg.message, "context": context, "source_ids": source_ids})
        return result
    except Exception as e:
        return {"answer": f"Agent error: {str(e)}", "sources": []}