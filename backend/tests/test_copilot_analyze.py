from fastapi.testclient import TestClient

from app.db.database import SessionLocal, engine
from app.db import models
from app.main import app


client = TestClient(app)


def setup_function():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)


def test_analyze_returns_resolve_with_sources(monkeypatch):
    db = SessionLocal()
    business = models.Business(name="Internal Ops")
    db.add(business)
    db.commit()
    db.refresh(business)

    db.add(
        models.KnowledgeItem(
            business_id=business.id,
            title="Reset de contraseña",
            content="Para resetear la contraseña hay que usar el enlace 'Olvidé mi contraseña'.",
        )
    )
    db.commit()
    db.close()

    monkeypatch.setattr(
        "app.api.copilot.generate_chat_reply",
        lambda _: "Puedes usar el enlace de recuperación de contraseña.",
    )

    resp = client.post(
        "/copilot/analyze",
        json={"title": "No puedo entrar", "body": "No puedo acceder a mi cuenta, olvidé mi contraseña"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "RESOLVE"
    assert data["confidence_score"] >= 0.35
    assert data["sources"]
    assert data["escalation_reason"] is None


def test_analyze_returns_escalate_without_knowledge():
    resp = client.post(
        "/copilot/analyze",
        json={"body": "Tengo un problema raro que nadie documentó"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "ESCALATE"
    assert data["escalation_reason"] == "insufficient_knowledge_match"
