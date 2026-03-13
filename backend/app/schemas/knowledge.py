from pydantic import BaseModel


class KnowledgeCreate(BaseModel):
    title: str
    content: str


class KnowledgeResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True