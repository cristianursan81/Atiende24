from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Business, BusinessSettings
from app.schemas.settings import BusinessSettingsCreate

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_or_update_settings(data: BusinessSettingsCreate, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == data.business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="El negocio no existe.")

    settings = (
        db.query(BusinessSettings)
        .filter(BusinessSettings.business_id == data.business_id)
        .first()
    )

    if settings is None:
        settings = BusinessSettings(
            business_id=data.business_id,
            assistant_name=data.assistant_name.strip(),
            tone=data.tone.strip(),
            welcome_message=data.welcome_message.strip(),
            fallback_message=data.fallback_message.strip(),
            system_prompt=data.system_prompt.strip() if data.system_prompt else None
        )
        db.add(settings)
    else:
        settings.assistant_name = data.assistant_name.strip()
        settings.tone = data.tone.strip()
        settings.welcome_message = data.welcome_message.strip()
        settings.fallback_message = data.fallback_message.strip()
        settings.system_prompt = data.system_prompt.strip() if data.system_prompt else None

    db.commit()
    db.refresh(settings)

    return {
        "business_id": settings.business_id,
        "assistant_name": settings.assistant_name,
        "tone": settings.tone,
        "welcome_message": settings.welcome_message,
        "fallback_message": settings.fallback_message,
        "system_prompt": settings.system_prompt
    }


@router.get("/{business_id}")
def get_settings(business_id: int, db: Session = Depends(get_db)):
    settings = (
        db.query(BusinessSettings)
        .filter(BusinessSettings.business_id == business_id)
        .first()
    )

    if settings is None:
        raise HTTPException(status_code=404, detail="Este negocio no tiene configuración todavía.")

    return {
        "business_id": settings.business_id,
        "assistant_name": settings.assistant_name,
        "tone": settings.tone,
        "welcome_message": settings.welcome_message,
        "fallback_message": settings.fallback_message,
        "system_prompt": settings.system_prompt
    }