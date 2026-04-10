from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    title: Optional[str] = None
    body: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    category: str
    confidence_score: float
    decision: str
    suggested_reply: str
    escalation_reason: Optional[str] = None
    sources: list[dict]
