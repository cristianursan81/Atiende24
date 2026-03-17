from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Business
from app.schemas.business import BusinessCreate

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_business(data: BusinessCreate, db: Session = Depends(get_db)):
    if not data.name or not data.name.strip():
        raise HTTPException(status_code=400, detail="El nombre del negocio no puede estar vacío.")

    business = Business(name=data.name.strip())
    db.add(business)
    db.commit()
    db.refresh(business)

    return {
        "id": business.id,
        "name": business.name,
        "created_at": business.created_at
    }


@router.get("/")
def list_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).order_by(Business.created_at.asc()).all()

    return [
        {
            "id": business.id,
            "name": business.name,
            "created_at": business.created_at
        }
        for business in businesses
    ]


@router.get("/{business_id}")
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()

    if business is None:
        raise HTTPException(status_code=404, detail="El negocio no existe.")

    return {
        "id": business.id,
        "name": business.name,
        "created_at": business.created_at
    }