"""
Minimum tests for the POST /copilot/analyze endpoint.

These tests run entirely in-process using FastAPI's TestClient and do not
require a live OpenAI key; the copilot service falls back to template-based
replies when the key is absent.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Schema / validation tests
# ---------------------------------------------------------------------------


def test_analyze_body_required():
    """Sending an empty body should return 422."""
    resp = client.post("/copilot/analyze", json={"body": ""})
    assert resp.status_code == 422


def test_analyze_body_missing():
    """Sending no body field at all should return 422."""
    resp = client.post("/copilot/analyze", json={"title": "Test"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Response structure tests
# ---------------------------------------------------------------------------


def test_analyze_returns_valid_structure():
    """A valid request should return all required fields."""
    resp = client.post(
        "/copilot/analyze",
        json={"title": "Horario", "body": "¿Cuál es vuestro horario de atención?"},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Required fields
    assert "category" in data
    assert "confidence_score" in data
    assert "decision" in data
    assert "suggested_reply" in data
    assert "escalation_reason" in data
    assert "reasoning_summary" in data
    assert "sources" in data


def test_analyze_category_is_valid():
    """category must be one of FAQ | PROCESS | ESCALATE."""
    resp = client.post(
        "/copilot/analyze",
        json={"body": "¿Cuánto tiempo tarda en llegar un pedido?"},
    )
    assert resp.status_code == 200
    assert resp.json()["category"] in ("FAQ", "PROCESS", "ESCALATE")


def test_analyze_confidence_range():
    """confidence_score must be between 0 and 1 inclusive."""
    resp = client.post(
        "/copilot/analyze",
        json={"body": "Necesito información sobre vuestros productos."},
    )
    assert resp.status_code == 200
    score = resp.json()["confidence_score"]
    assert 0.0 <= score <= 1.0


def test_analyze_decision_values():
    """decision must be either auto_reply or escalate."""
    resp = client.post(
        "/copilot/analyze",
        json={"body": "¿Cuáles son los métodos de pago disponibles?"},
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] in ("auto_reply", "escalate")


def test_analyze_sources_is_list():
    """sources must be a list."""
    resp = client.post(
        "/copilot/analyze",
        json={"body": "¿Cómo puedo devolver un producto?"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json()["sources"], list)


# ---------------------------------------------------------------------------
# Category-specific behaviour tests
# ---------------------------------------------------------------------------


def test_faq_ticket_gets_auto_reply():
    """A simple FAQ ticket about opening hours should get an auto_reply."""
    resp = client.post(
        "/copilot/analyze",
        json={"title": "Horario de atención", "body": "¿Cuál es el horario de atención al cliente?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "auto_reply"
    assert data["suggested_reply"] is not None
    assert len(data["sources"]) > 0


def test_process_ticket_categorised_correctly():
    """A how-to (process) ticket should be categorised as PROCESS."""
    resp = client.post(
        "/copilot/analyze",
        json={
            "title": "Quiero devolver un artículo",
            "body": "¿Cuál es el proceso para devolver un producto que compré la semana pasada?",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "PROCESS"


def test_escalation_ticket_triggers_escalate():
    """A ticket with escalation keywords should be escalated."""
    resp = client.post(
        "/copilot/analyze",
        json={
            "title": "Cobro duplicado urgente",
            "body": "Me habéis cobrado dos veces el pedido. Es urgente y voy a presentar una reclamación.",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "ESCALATE"
    assert data["decision"] == "escalate"
    assert data["escalation_reason"] is not None


def test_escalate_has_no_kb_sources():
    """When escalating, sources should be empty (no auto KB reply is generated)."""
    resp = client.post(
        "/copilot/analyze",
        json={
            "body": "Esto es urgente, quiero hablar con un abogado sobre esta reclamación.",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "ESCALATE"
    assert data["sources"] == []


def test_title_optional_no_title():
    """Request without title should work fine and return a valid response."""
    resp = client.post(
        "/copilot/analyze",
        json={"body": "¿Cuánto tarda en llegar mi pedido a las Islas Canarias?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] in ("FAQ", "PROCESS", "ESCALATE")


# ---------------------------------------------------------------------------
# Retrieval tests (unit level)
# ---------------------------------------------------------------------------


def test_retrieve_kb_returns_results():
    """retrieve_kb should return results for a known query."""
    from app.services.copilot_service import retrieve_kb

    results = retrieve_kb("horario atención cliente", top_k=3)
    assert len(results) > 0
    titles = [entry["title"] for entry, _ in results]
    assert any("horario" in t.lower() or "atención" in t.lower() for t in titles)


def test_retrieve_kb_top_k_respected():
    """retrieve_kb should never return more than top_k entries."""
    from app.services.copilot_service import retrieve_kb

    results = retrieve_kb("envío pedido entrega", top_k=2)
    assert len(results) <= 2


def test_confidence_zero_for_no_match():
    """A completely unrelated query should produce near-zero confidence."""
    from app.services.copilot_service import _confidence

    assert _confidence(0, 5) == 0.0
