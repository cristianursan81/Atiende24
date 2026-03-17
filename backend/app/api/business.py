from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import generate_api_key
from app.db.database import get_db
from app.db.models import Business
from app.schemas.business import BusinessCreate

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"]
)


@router.post("/")
def create_business(data: BusinessCreate, db: Session = Depends(get_db)):
    if not data.name or not data.name.strip():
        raise HTTPException(status_code=400, detail="El nombre del negocio no puede estar vacío.")

    business = Business(
        name=data.name.strip(),
        api_key=generate_api_key()
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    return {
        "id": business.id,
        "name": business.name,
        "api_key": business.api_key,
        "created_at": business.created_at
    }


@router.get("/")
def list_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).order_by(Business.created_at.asc()).all()

    return [
        {
            "id": business.id,
            "name": business.name,
            "api_key": business.api_key,
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
        "api_key": business.api_key,
        "created_at": business.created_at
    }