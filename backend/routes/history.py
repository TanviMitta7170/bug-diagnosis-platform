import json
import os
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/history", tags=["History"])

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bug_history.json")

def load_history() -> list:
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(history: list):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

@router.get("/all")
def get_history():
    return {"history": load_history()}

@router.post("/add")
def add_to_history(entry: dict):
    history         = load_history()
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry["id"]     = f"ANALYSIS-{len(history)+1:03d}"
    history.insert(0, entry)
    save_history(history[:50])
    return {"status": "saved", "id": entry["id"]}

@router.delete("/{entry_id}")
def delete_entry(entry_id: str):
    history = [h for h in load_history() if h.get("id") != entry_id]
    save_history(history)
    return {"status": "deleted"}

@router.put("/resolve/{entry_id}")
def mark_resolved(entry_id: str, notes: dict):
    history = load_history()
    for h in history:
        if h.get("id") == entry_id:
            h["status"]           = "Resolved"
            h["resolution_notes"] = notes.get("notes", "")
            h["applied_fix"]      = notes.get("applied_fix", "")
            h["resolved_at"]      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(history)
    return {"status": "resolved"}
