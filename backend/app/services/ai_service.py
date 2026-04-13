from openai import OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY no está configurada.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def generate_chat_reply(messages: list[dict]) -> str:
    response = _get_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
