from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import KnowledgeItem
from app.schemas.copilot import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import generate_chat_reply
from app.services.rag_service import retrieve_relevant_knowledge, score_knowledge_item

router = APIRouter(prefix="/copilot", tags=["copilot"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def classify_category(text: str) -> str:
    text_l = text.lower()
    if any(k in text_l for k in ["factura", "pago", "cobro", "reembolso"]):
        return "billing"
    if any(k in text_l for k in ["error", "fallo", "no funciona", "bug", "caída"]):
        return "technical"
    if any(k in text_l for k in ["cuenta", "contraseña", "acceso", "login"]):
        return "account"
    return "general"


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_ticket(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=400, detail="body no puede estar vacío")

    full_text = f"{(payload.title or '').strip()}\n{body}".strip()

    knowledge_items = (
        db.query(KnowledgeItem)
        .order_by(KnowledgeItem.created_at.asc())
        .all()
    )

    relevant_items = retrieve_relevant_knowledge(
        user_query=full_text,
        knowledge_items=knowledge_items,
        top_k=3,
    )

    # Heurística simple de confianza basada en solapamiento léxico
    raw_scores = [
        score_knowledge_item(full_text, item.title, item.content)
        for item in relevant_items
    ]
    avg_score = (sum(raw_scores) / len(raw_scores)) if raw_scores else 0.0
    confidence_score = round(min(1.0, avg_score / 3.0), 2)

    category = classify_category(full_text)
    sources = [{"id": item.id, "title": item.title} for item in relevant_items]

    # Decisión básica: si no hay base suficiente => escalar
    if not relevant_items or confidence_score < 0.35:
        return AnalyzeResponse(
            category=category,
            confidence_score=confidence_score,
            decision="ESCALATE",
            suggested_reply=(
                "Necesito escalar este caso al equipo humano para darte una respuesta precisa."
            ),
            escalation_reason="insufficient_knowledge_match",
            sources=sources,
        )

    knowledge_context = "\n\n".join(
        [f"{item.title}: {item.content}" for item in relevant_items]
    )

    messages_for_ai = [
        {
            "role": "system",
            "content": (
                "Eres un AI Support Copilot interno para agentes de soporte. "
                "Redacta una respuesta sugerida breve, clara y accionable basada solo en la evidencia proporcionada. "
                "Si falta información, dilo explícitamente y recomienda escalado. "
                f"\n\nFUENTES INTERNAS:\n{knowledge_context}"
            ),
        },
        {
            "role": "user",
            "content": f"Ticket:\n{full_text}",
        },
    ]

    try:
        suggested_reply = generate_chat_reply(messages_for_ai)
    except Exception:
        # Fallback para no romper el flujo MVP
        suggested_reply = (
            "Según la base de conocimiento interna, este caso parece resoluble. "
            "Revisa las fuentes sugeridas antes de enviar la respuesta final."
        )

    return AnalyzeResponse(
        category=category,
        confidence_score=confidence_score,
        decision="RESOLVE",
        suggested_reply=suggested_reply,
        escalation_reason=None,
        sources=sources,
    )
