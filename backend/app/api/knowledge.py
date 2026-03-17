from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_api_key, validate_api_key_for_business
from app.db.database import get_db
from app.db.models import KnowledgeItem
from app.schemas.knowledge import KnowledgeCreate

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"]
)


@router.post("/")
def create_knowledge_item(
    data: KnowledgeCreate,
    db: Session = Depends(get_db),
    x_api_key: str | None = Depends(get_api_key)
):
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="El título no puede estar vacío.")
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="El contenido no puede estar vacío.")

    validate_api_key_for_business(data.business_id, x_api_key, db)

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
    db: Session = Depends(get_db),
    x_api_key: str | None = Depends(get_api_key)
):
    validate_api_key_for_business(business_id, x_api_key, db)

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