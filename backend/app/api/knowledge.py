from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Business, KnowledgeItem
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

    business = db.query(Business).filter(Business.id == data.business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="El negocio no existe.")

    item = KnowledgeItem(
        business_id=data.business_id,
        title=data.title.strip(),
        content=data.content.strip()
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "business_id": item.business_id,
        "title": item.title,
        "content": item.content
    }


@router.get("/")
def list_knowledge_items(
    business_id: int = Query(...),
    db: Session = Depends(get_db)
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="El negocio no existe.")

    items = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.business_id == business_id)
        .order_by(KnowledgeItem.created_at.asc())
        .all()
    )

    return [
        {
            "id": item.id,
            "business_id": item.business_id,
            "title": item.title,
            "content": item.content
        }
        for item in items
    ]