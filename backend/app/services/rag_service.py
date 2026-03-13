import re
from collections import Counter


STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "en", "y", "o", "u", "que",
    "es", "son", "por", "para", "con", "sin", "se", "su",
    "sus", "mi", "mis", "tu", "tus", "nuestro", "nuestra",
    "vuestro", "vuestra", "qué", "cual", "cuál", "donde",
    "dónde", "como", "cómo", "cuando", "cuándo", "tenéis",
    "tienen", "hay", "hola", "buenas", "buenos"
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sáéíóúüñ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = normalized.split()
    return [token for token in tokens if token not in STOPWORDS_ES and len(token) > 1]


def score_knowledge_item(user_query: str, title: str, content: str) -> int:
    query_tokens = tokenize(user_query)
    item_tokens = tokenize(f"{title} {content}")

    if not query_tokens or not item_tokens:
        return 0

    query_counter = Counter(query_tokens)
    item_counter = Counter(item_tokens)

    score = 0
    for token, count in query_counter.items():
        score += min(count, item_counter.get(token, 0))

    return score


def retrieve_relevant_knowledge(user_query: str, knowledge_items: list, top_k: int = 3):
    scored_items = []

    for item in knowledge_items:
        score = score_knowledge_item(user_query, item.title, item.content)
        scored_items.append((item, score))

    # ordenar por score descendente
    scored_items.sort(key=lambda x: x[1], reverse=True)

    # quedarnos solo con los que aportan algo
    filtered = [item for item, score in scored_items if score > 0]

    # si no hay coincidencias, devolver algunos pocos por defecto
    if not filtered:
        return knowledge_items[:top_k]

    return filtered[:top_k]