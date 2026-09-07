from fastapi import APIRouter
from models.bug_report import CommitInput
from agents import prediction_agent

router = APIRouter(prefix="/api", tags=["Prediction"])

@router.post("/predict")
async def predict_risk(commit: CommitInput):
    result = await prediction_agent.run(commit.model_dump())
    return {"status": "complete", "result": result}
