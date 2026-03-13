import unittest
from unittest.mock import patch

from app.services import ai_service


class AIServiceTests(unittest.TestCase):
    def setUp(self):
        ai_service._client = None

    def tearDown(self):
        ai_service._client = None

    @patch("app.services.ai_service.OPENAI_API_KEY", None)
    def test_get_openai_client_raises_when_api_key_missing(self):
        with self.assertRaises(RuntimeError) as ctx:
            ai_service.get_openai_client()

        self.assertEqual(str(ctx.exception), "OPENAI_API_KEY no está configurada.")


if __name__ == "__main__":
    unittest.main()
