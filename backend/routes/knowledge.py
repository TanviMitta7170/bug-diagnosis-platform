import json
from fastapi import APIRouter, HTTPException
from models.bug_report import ResolvedBug
from models.analysis_result import KBResponse
from config import SEED_DATA_PATH

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

def load_bugs() -> list:
    with open(SEED_DATA_PATH, "r") as f:
        return json.load(f)

def save_bugs(bugs: list):
    with open(SEED_DATA_PATH, "w") as f:
        json.dump(bugs, f, indent=2)

@router.get("/bugs")
def get_all_bugs():
    bugs = load_bugs()
    return {"total": len(bugs), "bugs": bugs}

@router.get("/count")
def get_count():
    return {"count": len(load_bugs())}

@router.post("/add", response_model=KBResponse)
def add_bug(bug: ResolvedBug):
    bugs = load_bugs()
    if any(b["id"] == bug.id for b in bugs):
        raise HTTPException(status_code=400, detail=f"Bug {bug.id} already exists")
    bugs.append(bug.model_dump())
    save_bugs(bugs)
    return KBResponse(success=True, message=f"Bug {bug.id} added to knowledge base", total_bugs=len(bugs))
