from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_api_key, validate_api_key_for_business
from app.db.database import get_db
from app.db.models import BusinessSettings
from app.schemas.settings import BusinessSettingsCreate

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


@router.post("/")
def create_or_update_settings(
    data: BusinessSettingsCreate,
    db: Session = Depends(get_db),
    x_api_key: str | None = Depends(get_api_key)
):
    validate_api_key_for_business(data.business_id, x_api_key, db)

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
def get_settings(
    business_id: int,
    db: Session = Depends(get_db),
    x_api_key: str | None = Depends(get_api_key)
):
    validate_api_key_for_business(business_id, x_api_key, db)

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