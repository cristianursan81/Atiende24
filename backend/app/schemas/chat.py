from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    business_id: int
    message: str
    conversation_id: Optional[int] = None