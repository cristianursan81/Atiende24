from typing import List, Literal, Optional

from pydantic import BaseModel, field_validator


class CopilotRequest(BaseModel):
    title: Optional[str] = None
    body: str

    @field_validator("body")
    @classmethod
    def body_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("body cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class KBSource(BaseModel):
    title: str
    content: str


class CopilotResponse(BaseModel):
    category: Literal["FAQ", "PROCESS", "ESCALATE"]
    confidence_score: float
    decision: Literal["auto_reply", "escalate"]
    suggested_reply: Optional[str] = None
    escalation_reason: Optional[str] = None
    reasoning_summary: str
    sources: List[KBSource]
