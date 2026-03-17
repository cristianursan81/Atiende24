from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import business, chat, knowledge, settings, templates, leads, analytics, crm, business_hours, product_catalog, chat_sessions
from app.db.database import engine
from app.db import models
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

print("MODEL:", OPENAI_MODEL)
print("API KEY LEIDA:", OPENAI_API_KEY[:15] if OPENAI_API_KEY else "VACIA")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Atiende24 API",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "null"  # For file:// protocol
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(settings.router)
app.include_router(business.router)
app.include_router(templates.router)
app.include_router(leads.router)
app.include_router(analytics.router)
app.include_router(crm.router)
app.include_router(business_hours.router)
app.include_router(product_catalog.router)
app.include_router(chat_sessions.router)


@app.get("/")
def root():
    return {"status": "Atiende24 backend running"}