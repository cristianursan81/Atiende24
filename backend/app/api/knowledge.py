from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import KnowledgeItem
from app.schemas.knowledge import KnowledgeCreate

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_knowledge_item(data: KnowledgeCreate, db: Session = Depends(get_db)):
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="El título no puede estar vacío.")
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="El contenido no puede estar vacío.")

    item = KnowledgeItem(
        title=data.title.strip(),
        content=data.content.strip()
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "title": item.title,
        "content": item.content
    }


@router.get("/")
def list_knowledge_items(db: Session = Depends(get_db)):
    items = db.query(KnowledgeItem).order_by(KnowledgeItem.created_at.asc()).all()

    return [
        {
            "id": item.id,
            "title": item.title,
            "content": item.content
        }
        for item in items
    ]