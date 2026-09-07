from pydantic import BaseModel
from typing import Any, Optional

class AgentResult(BaseModel):
    agent:  str
    status: str
    output: dict[str, Any]

class AnalysisResult(BaseModel):
    bug_id:  str
    results: list[AgentResult]

class KBResponse(BaseModel):
    success:    bool
    message:    str
    total_bugs: int

class ChatResponse(BaseModel):
    answer:  str
    sources: list[str]
