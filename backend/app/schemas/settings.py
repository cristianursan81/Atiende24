from pydantic import BaseModel
from typing import Optional


class BusinessSettingsCreate(BaseModel):
    business_id: int
    assistant_name: str = "Asistente virtual"
    tone: str = "professional"
    welcome_message: str = "Hola, ¿en qué puedo ayudarte?"
    fallback_message: str = "Lo siento, no dispongo de esa información en este momento."
    system_prompt: Optional[str] = None