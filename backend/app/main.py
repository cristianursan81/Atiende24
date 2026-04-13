from fastapi import FastAPI

from app.api import chat, knowledge, copilot
from app.db.database import engine
from app.db import models
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

print("MODEL:", OPENAI_MODEL)
print("API KEY CONFIGURADA:", "sí" if OPENAI_API_KEY else "no")

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
