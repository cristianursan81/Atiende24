"""
Copilot service for Atiende24.

Responsibilities:
- Retrieve relevant knowledge-base entries for a support ticket.
- Determine category (FAQ | PROCESS | ESCALATE).
- Calculate a confidence score.
- Apply escalation rules.
- Generate a suggested reply (via OpenAI when available, template otherwise).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import List, Optional, Tuple

from app.data.demo_kb import DEMO_KB, KBEntry
from app.schemas.copilot import CopilotResponse, KBSource

# ---------------------------------------------------------------------------
# Stopwords (Spanish)
# ---------------------------------------------------------------------------

_STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "en", "y", "o", "u", "que", "es",
    "son", "por", "para", "con", "sin", "se", "su", "sus", "mi",
    "mis", "tu", "tus", "nuestro", "nuestra", "vuestro",
    "qué", "cual", "cuál", "donde", "dónde", "como", "cómo",
    "cuando", "cuándo", "tenéis", "tienen", "hay", "hola",
    "buenas", "buenos", "me", "nos", "le", "les", "lo",
    "este", "esta", "estos", "estas", "ese", "esa", "eso",
}

# ---------------------------------------------------------------------------
# Escalation keyword sets
# ---------------------------------------------------------------------------

_ESCALATION_KEYWORDS = {
    "urgente", "urgencia", "queja", "reclamacion", "reclamación",
    "fraude", "robo", "amenaza", "legal", "abogado", "denuncia",
    "cobro indebido", "error grave", "inaceptable", "imperdonable",
    "accidente", "lesión", "lesion", "emergencia", "daños", "daño",
    "roto", "destrozado", "incumplimiento", "dos veces", "cobrado dos",
    "doble cobro",
}

# Process-type ticket keywords
_PROCESS_KEYWORDS = {
    "proceso", "pasos", "procedimiento", "cambio", "cancelar",
    "cancelación", "cancelacion", "tramitar", "solicitar", "devolver",
    "devolución", "devolucion", "gestionar", "rastrear", "seguimiento",
    "como", "cómo",
}

# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sáéíóúüñ]", " ", text)
    return re.sub(r"\s+", " ", text)


def _tokenize(text: str) -> List[str]:
    tokens = _normalize(text).split()
    return [t for t in tokens if t not in _STOPWORDS_ES and len(t) > 1]


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------


def _score(query_tokens: List[str], title: str, content: str) -> int:
    """Keyword overlap score between query and a KB entry."""
    item_tokens = _tokenize(f"{title} {content}")
    if not query_tokens or not item_tokens:
        return 0
    q_counter = Counter(query_tokens)
    i_counter = Counter(item_tokens)
    return sum(min(cnt, i_counter.get(tok, 0)) for tok, cnt in q_counter.items())


def retrieve_kb(query: str, top_k: int = 3) -> List[Tuple[KBEntry, int]]:
    """Return the top_k KB entries most relevant to *query*, with their scores."""
    tokens = _tokenize(query)
    scored = [
        (entry, _score(tokens, entry["title"], entry["content"]))
        for entry in DEMO_KB
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    # Keep only entries that contribute at least one keyword match
    relevant = [(e, s) for e, s in scored if s > 0]
    return relevant[:top_k] if relevant else scored[:top_k]


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------


def _confidence(top_score: int, query_token_count: int) -> float:
    """Sigmoid-like normalization to [0, 1]."""
    if top_score <= 0 or query_token_count == 0:
        return 0.0
    # Normalize relative to query length, then apply a soft cap via tanh
    raw = top_score / max(query_token_count, 1)
    score = math.tanh(raw * 1.5)
    return round(min(score, 1.0), 4)


# ---------------------------------------------------------------------------
# Escalation detection
# ---------------------------------------------------------------------------


def _has_escalation_signal(text: str) -> Optional[str]:
    """Return an escalation reason string if any escalation keywords are found."""
    lower = text.lower()
    for kw in _ESCALATION_KEYWORDS:
        if kw in lower:
            return f"El ticket contiene lenguaje que indica urgencia o reclamación formal: '{kw}'"
    return None


# ---------------------------------------------------------------------------
# Category classification
# ---------------------------------------------------------------------------


def _classify(query: str, confidence: float, escalation_reason: Optional[str]) -> str:
    if escalation_reason or confidence < 0.3:
        return "ESCALATE"
    tokens = set(_tokenize(query))
    if tokens & _PROCESS_KEYWORDS:
        return "PROCESS"
    return "FAQ"


# ---------------------------------------------------------------------------
# Reply generation
# ---------------------------------------------------------------------------

_REPLY_TEMPLATE = (
    "Hola, gracias por contactarnos.\n\n"
    "Según la información disponible:\n\n"
    "{sources_text}\n\n"
    "Si tienes más dudas, no dudes en escribirnos."
)

_ESCALATE_TEMPLATE = (
    "Hola, gracias por contactarnos.\n\n"
    "Tu consulta requiere la atención de un agente especializado. "
    "Te pondremos en contacto con el equipo correspondiente lo antes posible.\n\n"
    "Lamentamos los inconvenientes causados."
)


def _generate_reply_openai(query: str, sources: List[KBSource]) -> Optional[str]:
    """Try to generate a reply with OpenAI; return None on any failure."""
    try:
        from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

        if not OPENAI_API_KEY:
            return None

        from openai import OpenAI

        context = "\n\n".join(
            f"[{s.title}]: {s.content}" for s in sources
        )
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente de soporte al cliente. "
                    "Responde en español de forma clara, breve y profesional. "
                    "Usa exclusivamente la información del contexto proporcionado. "
                    "No inventes datos. Si la información no está disponible, indícalo."
                    f"\n\nCONTEXTO DE CONOCIMIENTO:\n{context}"
                ),
            },
            {"role": "user", "content": query},
        ]
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt_messages,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def _generate_reply_template(sources: List[KBSource]) -> str:
    """Fallback template-based reply built from source content."""
    if not sources:
        return (
            "Hola, gracias por contactarnos. "
            "En este momento no dispongo de información específica para responder a tu consulta. "
            "Un agente te contactará próximamente."
        )
    sources_text = "\n\n".join(
        f"• {s.title}: {s.content}" for s in sources
    )
    return _REPLY_TEMPLATE.format(sources_text=sources_text)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def analyze_ticket(title: Optional[str], body: str) -> CopilotResponse:
    """
    Analyze a support ticket and return a structured CopilotResponse.

    Parameters
    ----------
    title:
        Optional ticket title (may be None or empty).
    body:
        Mandatory ticket body text.
    """
    query = f"{title or ''} {body}".strip()

    # 1. Retrieve relevant KB entries
    retrieved = retrieve_kb(query, top_k=3)
    sources = [
        KBSource(title=entry["title"], content=entry["content"])
        for entry, _ in retrieved
    ]
    top_score = retrieved[0][1] if retrieved else 0

    # 2. Confidence
    query_tokens = _tokenize(query)
    confidence = _confidence(top_score, len(query_tokens))

    # 3. Escalation check
    escalation_reason = _has_escalation_signal(query)

    # 4. Category
    category = _classify(query, confidence, escalation_reason)

    # Adjust sources to empty list when escalating (no KB reply needed)
    if category == "ESCALATE":
        sources_out: List[KBSource] = []
    else:
        sources_out = sources

    # 5. Decision
    decision = "escalate" if category == "ESCALATE" else "auto_reply"

    # 6. Suggested reply
    if decision == "escalate":
        suggested_reply: Optional[str] = _ESCALATE_TEMPLATE
    else:
        suggested_reply = (
            _generate_reply_openai(query, sources_out)
            or _generate_reply_template(sources_out)
        )

    # 7. Reasoning summary
    if category == "ESCALATE":
        reasoning_summary = (
            escalation_reason
            or f"Confianza baja ({confidence:.2f}): no se encontró conocimiento suficiente para responder automáticamente."
        )
    else:
        source_titles = ", ".join(s.title for s in sources_out) if sources_out else "ninguna"
        reasoning_summary = (
            f"Categoría detectada: {category}. "
            f"Confianza: {confidence:.2f}. "
            f"Fuentes consultadas: {source_titles}."
        )

    return CopilotResponse(
        category=category,
        confidence_score=confidence,
        decision=decision,
        suggested_reply=suggested_reply,
        escalation_reason=escalation_reason,
        reasoning_summary=reasoning_summary,
        sources=sources_out,
    )
