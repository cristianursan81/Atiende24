import logging

from fastapi import FastAPI

from app.api import chat, knowledge, copilot
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.db import models
from app.db.database import engine

logger = logging.getLogger(__name__)

if OPENAI_API_KEY:
    logger.info("MODEL: %s | API key leída: configurada", OPENAI_MODEL)
else:
    logger.warning("MODEL: %s | API key leída: no configurada", OPENAI_MODEL)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Atiende24 API",
    version="0.2",
    description=(
        "Atiende24 — AI Support Copilot.\n\n"
        "POST /copilot/analyze  →  analyze a ticket and get a structured AI response."
    ),
)

app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(copilot.router)


@app.get("/")
def root():
    return {"status": "Atiende24 backend running"}
