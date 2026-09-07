from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Environment(str, Enum):
    production  = "Production"
    staging     = "Staging"
    development = "Development"
    qa          = "QA"

class BugReport(BaseModel):
    log:         str              = Field(..., min_length=10)
    component:   Optional[str]   = Field("Unknown")
    environment: Optional[Environment] = Field(Environment.production)
    reporter:    Optional[str]   = Field("Anonymous")

class ResolvedBug(BaseModel):
    id:          str
    title:       str
    stack_trace: str
    root_cause:  str
    resolution:  str
    severity:    str
    priority:    str
    component:   str
    status:      str = "Resolved"

class CommitInput(BaseModel):
    commit_diff:    str           = Field(...)
    commit_message: Optional[str] = Field("")
    author:         Optional[str] = Field("Unknown")

class ChatMessage(BaseModel):
    message: str           = Field(...)
    bug_id:  Optional[str] = Field(None)
