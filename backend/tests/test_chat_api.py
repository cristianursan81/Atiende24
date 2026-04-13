import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.chat import get_db
from app.db.models import Base, Business, Conversation, KnowledgeItem, Message
from app.main import app


class ChatApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.TestSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

        # Create a test business
        db = cls.TestSessionLocal()
        try:
            business = Business(name="Negocio Test")
            db.add(business)
            db.commit()
            db.refresh(business)
            cls.business_id = business.id
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=cls.engine)

    def setUp(self):
        db = self.TestSessionLocal()
        try:
            db.query(Message).delete()
            db.query(KnowledgeItem).delete()
            db.query(Conversation).delete()
            db.commit()
        finally:
            db.close()

    @patch("app.api.chat.generate_chat_reply", return_value="Hola, ¿en qué puedo ayudarte?")
    def test_chat_message_creates_conversation_when_none(self, _mock_reply):
        response = self.client.post(
            "/chat/message",
            json={"business_id": self.business_id, "message": "Hola"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("conversation_id", payload)
        self.assertEqual(payload["reply"], "Hola, ¿en qué puedo ayudarte?")

    def test_chat_message_returns_404_for_unknown_conversation(self):
        response = self.client.post(
            "/chat/message",
            json={"business_id": self.business_id, "conversation_id": 9999, "message": "Hola"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "La conversación no existe.")

    def test_chat_message_returns_404_for_unknown_business(self):
        response = self.client.post(
            "/chat/message",
            json={"business_id": 9999, "message": "Hola"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "El negocio no existe.")

    def test_chat_message_returns_400_for_empty_message(self):
        response = self.client.post(
            "/chat/message",
            json={"business_id": self.business_id, "message": "   "},
        )

        self.assertEqual(response.status_code, 400)

    @patch("app.api.chat.generate_chat_reply", side_effect=RuntimeError("OPENAI_API_KEY no está configurada."))
    def test_chat_message_returns_500_when_ai_provider_fails(self, _mock_reply):
        response = self.client.post(
            "/chat/message",
            json={"business_id": self.business_id, "message": "Hola"},
        )

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
