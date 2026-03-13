import unittest
from types import SimpleNamespace

from app.services.rag_service import normalize_text, retrieve_relevant_knowledge, score_knowledge_item, tokenize


class RagServiceTests(unittest.TestCase):
    def test_normalize_text_removes_punctuation_and_lowercases(self):
        self.assertEqual(normalize_text(" ¡HÓLA!, Mundo... \n").strip(), "hóla mundo")

    def test_tokenize_removes_stopwords(self):
        tokens = tokenize("Hola, ¿cuál es vuestro horario de atención?")
        self.assertEqual(tokens, ["horario", "atención"])

    def test_score_knowledge_item_counts_shared_tokens(self):
        score = score_knowledge_item(
            user_query="horario horario tarde",
            title="Horario del local",
            content="Nuestro horario de tarde es de 16 a 20",
        )
        self.assertEqual(score, 3)

    def test_retrieve_relevant_knowledge_returns_ranked_top_k(self):
        items = [
            SimpleNamespace(title="Precios", content="Lista de precios actualizados"),
            SimpleNamespace(title="Horario", content="Abrimos de lunes a viernes"),
            SimpleNamespace(title="Ubicación", content="Estamos en el centro"),
        ]

        result = retrieve_relevant_knowledge("¿Cuál es el horario?", items, top_k=2)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Horario")

    def test_retrieve_relevant_knowledge_fallback_when_no_match(self):
        items = [
            SimpleNamespace(title="Horario", content="Abrimos de lunes a viernes"),
            SimpleNamespace(title="Ubicación", content="Estamos en el centro"),
            SimpleNamespace(title="Precios", content="Tarifas por servicio"),
        ]

        result = retrieve_relevant_knowledge("cotización para evento corporativo", items, top_k=2)

        self.assertEqual(result, items[:2])


if __name__ == "__main__":
    unittest.main()
