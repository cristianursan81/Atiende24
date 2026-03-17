from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_api_key, validate_api_key_for_business
from app.db.database import get_db
from app.db.models import BusinessSettings, Conversation, Message, KnowledgeItem
from app.schemas.chat import ChatRequest
from app.services.ai_service import generate_chat_reply
from app.services.rag_service import retrieve_relevant_knowledge

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/message")
def chat_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    x_api_key: str | None = Depends(get_api_key)
):
    if not data.message or not data.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    business = validate_api_key_for_business(data.business_id, x_api_key, db)

    settings = (
        db.query(BusinessSettings)
        .filter(BusinessSettings.business_id == data.business_id)
        .first()
    )

    # Crear o recuperar conversación
    if data.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == data.conversation_id)
            .first()
        )

        if conversation is None:
            raise HTTPException(status_code=404, detail="La conversación no existe.")

        if conversation.business_id != data.business_id:
            raise HTTPException(status_code=403, detail="La conversación no pertenece a este negocio.")
    else:
        conversation = Conversation(business_id=data.business_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Guardar mensaje del usuario
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=data.message.strip()
    )
    db.add(user_message)
    db.commit()

    # Recuperar historial reciente
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    recent_history = history[-10:]

    # Recuperar conocimiento solo del negocio actual
    knowledge_items = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.business_id == data.business_id)
        .order_by(KnowledgeItem.created_at.asc())
        .all()
    )

    relevant_items = retrieve_relevant_knowledge(
        user_query=data.message.strip(),
        knowledge_items=knowledge_items,
        top_k=3
    )

    knowledge_context = "\n\n".join(
        [f"{item.title}: {item.content}" for item in relevant_items]
    )

    if not knowledge_context:
        knowledge_context = "No hay conocimiento del negocio cargado todavía."

    assistant_name = settings.assistant_name if settings else "Asistente virtual"
    tone = settings.tone if settings else "professional"
    fallback_message = (
        settings.fallback_message
        if settings else "Lo siento, no dispongo de esa información en este momento."
    )
    extra_system_prompt = settings.system_prompt if settings and settings.system_prompt else ""

    system_prompt = (
        f"Eres {assistant_name}, el asistente virtual de {business.name} dentro de Atiende24. "
        f"Responde siempre en español, con un tono {tone}, de forma clara, breve, útil y profesional. "
        "Debes responder usando prioritariamente el conocimiento del negocio que se te proporciona. "
        "No inventes horarios, precios, direcciones, políticas ni servicios. "
        f"Si la información no aparece de forma clara en el conocimiento, responde exactamente con: {fallback_message}. "
    )

    if extra_system_prompt:
        system_prompt += f"Instrucciones adicionales: {extra_system_prompt} "

    system_prompt += f"\n\nCONOCIMIENTO RELEVANTE DEL NEGOCIO:\n{knowledge_context}"

    messages_for_ai = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for msg in recent_history:
        messages_for_ai.append(
            {
                "role": msg.role,
                "content": msg.content
            }
        )

    # Generar respuesta
    try:
        reply_text = generate_chat_reply(messages_for_ai)
    except Exception as e:
        print("ERROR OPENAI / CHAT:", repr(e))
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta con OpenAI: {str(e)}")

    # Guardar respuesta del asistente
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply_text
    )
    db.add(assistant_message)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "business_id": business.id,
        "reply": reply_text
    }