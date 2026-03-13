from pydantic import BaseModel


class KnowledgeCreate(BaseModel):
    business_id: int
    title: str
    content: str