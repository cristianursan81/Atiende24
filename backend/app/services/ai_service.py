from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_chat_reply(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()