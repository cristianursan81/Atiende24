from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Conversation, KnowledgeItem, Message
from app.services.ai_service import generate_chat_reply
from app.services.rag_service import retrieve_relevant_knowledge

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/message")
def chat_message(data: ChatRequest, db: Session = Depends(get_db)):
    if not data.message or not data.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    # Crear o recuperar conversación
    if data.conversation_id is not None:
        conversation = db.query(Conversation).filter(Conversation.id == data.conversation_id).first()
        if conversation is None:
            raise HTTPException(status_code=404, detail="La conversación indicada no existe.")
    else:
        conversation = Conversation()
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

    # Recuperar conocimiento y seleccionar solo lo relevante
    knowledge_items = db.query(KnowledgeItem).order_by(KnowledgeItem.created_at.asc()).all()

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

    # Construir prompt para OpenAI
    messages_for_ai = [
        {
            "role": "system",
            "content": (
                "Eres el asistente virtual de un negocio dentro de Atiende24. "
                "Responde siempre en español, de forma clara, breve, útil y profesional. "
                "Debes responder usando prioritariamente el conocimiento del negocio que se te proporciona. "
                "No inventes horarios, precios, direcciones, políticas ni servicios. "
                "Si la información no aparece de forma clara en el conocimiento, dilo con honestidad. "
                "Cuando corresponda, invita al usuario a dejar sus datos para que el negocio le contacte. "
                f"\n\nCONOCIMIENTO RELEVANTE DEL NEGOCIO:\n{knowledge_context}"
            )
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
        "reply": reply_text
    }
from fastapi import APIRouter, Depends, HTTPExceptionfrom pydantic import BaseModelfrom sqlalchemy.orm import Sessionfrom app.db.database import SessionLocalfrom app.db.models import Conversation, Message, KnowledgeItemfrom app.services.ai_service import generate_chat_replyfrom app.services.rag_service import retrieve_relevant_knowledgerouter = APIRouter(    prefix="/chat",    tags=["chat"])class ChatRequest(BaseModel):    message: str    conversation_id: Optional[int] = Nonedef get_db():    db = SessionLocal()    try:        yield db    finally:        db.close()@router.post("/message")def chat_message(data: ChatRequest, db: Session = Depends(get_db)):    if not data.message or not data.message.strip():        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")    # Crear o recuperar conversación    if data.conversation_id:        conversation = db.query(Conversation).filter(Conversation.id == data.conversation_id).first()        if conversation is None:            conversation = Conversation()            db.add(conversation)            db.commit()            db.refresh(conversation)    else:        conversation = Conversation()        db.add(conversation)        db.commit()        db.refresh(conversation)    # Guardar mensaje del usuario    user_message = Message(        conversation_id=conversation.id,        role="user",        content=data.message.strip()    )    db.add(user_message)    db.commit()    # Recuperar historial reciente    history = (        db.query(Message)        .filter(Message.conversation_id == conversation.id)        .order_by(Message.created_at.asc())        .all()    )    recent_history = history[-10:]    # Recuperar conocimiento y seleccionar solo lo relevante    knowledge_items = db.query(KnowledgeItem).order_by(KnowledgeItem.created_at.asc()).all()    relevant_items = retrieve_relevant_knowledge(        user_query=data.message.strip(),        knowledge_items=knowledge_items,        top_k=3    )    knowledge_context = "\n\n".join(        [f"{item.title}: {item.content}" for item in relevant_items]    )    if not knowledge_context:        knowledge_context = "No hay conocimiento del negocio cargado todavía."    # Construir prompt para OpenAI    messages_for_ai = [        {            "role": "system",            "content": (                "Eres el asistente virtual de un negocio dentro de Atiende24. "                "Responde siempre en español, de forma clara, breve, útil y profesional. "                "Debes responder usando prioritariamente el conocimiento del negocio que se te proporciona. "                "No inventes horarios, precios, direcciones, políticas ni servicios. "                "Si la información no aparece de forma clara en el conocimiento, dilo con honestidad. "                "Cuando corresponda, invita al usuario a dejar sus datos para que el negocio le contacte. "                f"\n\nCONOCIMIENTO RELEVANTE DEL NEGOCIO:\n{knowledge_context}"            )        }    ]    for msg in recent_history:        messages_for_ai.append(            {                "role": msg.role,                "content": msg.content            }        )    # Generar respuesta    try:        reply_text = generate_chat_reply(messages_for_ai)    except Exception as e:        print("ERROR OPENAI / CHAT:", repr(e))        raise HTTPException(status_code=500, detail=f"Error al generar respuesta con OpenAI: {str(e)}")    # Guardar respuesta del asistente    assistant_message = Message(        conversation_id=conversation.id,        role="assistant",        content=reply_text    )    db.add(assistant_message)    db.commit()    return {        "conversation_id": conversation.id,        "reply": reply_text    }