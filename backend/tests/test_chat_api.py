import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.chat import get_db
from app.db.models import Base, Conversation, KnowledgeItem, Message
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
        response = self.client.post("/chat/message", json={"message": "Hola"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("conversation_id", payload)
        self.assertEqual(payload["reply"], "Hola, ¿en qué puedo ayudarte?")

    def test_chat_message_returns_404_for_unknown_conversation(self):
        response = self.client.post(
            "/chat/message",
            json={"conversation_id": 9999, "message": "Hola"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "La conversación indicada no existe.")


if __name__ == "__main__":
    unittest.main()
