import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.models import Business


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    return secrets.token_hex(24)


def get_api_key(x_api_key: str | None = Security(api_key_header)) -> str | None:
    return x_api_key


def validate_api_key_for_business(
    business_id: int,
    x_api_key: str | None,
    db: Session
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Falta el header X-API-Key.")

    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="El negocio no existe.")

    if business.api_key != x_api_key:
        raise HTTPException(status_code=403, detail="API key inválida para este negocio.")

    return business