# Atiende24
AI Receptionist Platform for Local Businesses

Atiende24 es una plataforma SaaS que permite a negocios locales automatizar su atención al cliente mediante agentes de inteligencia artificial capaces de responder preguntas, gestionar conversaciones y utilizar el conocimiento del negocio.

Ejemplos de uso:

- clínicas dentales
- peluquerías
- restaurantes
- academias
- centros médicos
- gimnasios

El sistema funciona como una **recepcionista virtual 24/7**.

---

# Arquitectura del sistema

Atiende24 está construido con una arquitectura modular basada en API.

Cliente (Swagger / Web Widget)
        │
        ▼
FastAPI Backend
        │
        ├── Chat API
        ├── Knowledge API
        │
        ▼
SQLite Database
        │
        ├── Conversations
        ├── Messages
        ├── KnowledgeItems
        │
        ▼
RAG Engine
        │
        ├── Embeddings
        ├── Similarity Search
        │
        ▼
OpenAI LLM

---

# Stack tecnológico

Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- OpenAI API
- python-dotenv

IA

Modelo de chat

gpt-4o-mini

Modelo de recuperación de conocimiento

Búsqueda léxica por tokens (sin embeddings en el MVP actual)

---

# Estructura del proyecto

Atiende24
│
├── backend
│   │
│   ├── app
│   │   │
│   │   ├── api
│   │   │   ├── chat.py
│   │   │   └── knowledge.py
│   │   │
│   │   ├── core
│   │   │   └── config.py
│   │   │
│   │   ├── db
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   │
│   │   ├── schemas
│   │   │   └── knowledge.py
│   │   │
│   │   └── services
│   │       ├── ai_service.py
│   │       └── rag_service.py
│   │
│   ├── .env
│   ├── atiende24.db
│   ├── requirements.txt
│   └── run.py

---

# Variables de entorno

Archivo

backend/.env

Contenido

OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4o-mini

---

# Instalación

1 instalar dependencias

pip install -r requirements.txt

2 arrancar servidor

python run.py

Servidor disponible en

http://localhost:8000

Documentación automática

http://localhost:8000/docs

---

# API endpoints

Chat

POST /chat/message

Input

{
  "conversation_id": 1,
  "message": "¿Cuál es vuestro horario?"
}

Respuesta

{
  "conversation_id": 1,
  "reply": "Abrimos de lunes a viernes de 9 a 19."
}

---

Knowledge base

Crear conocimiento

POST /knowledge/

{
  "title": "Horario",
  "content": "Abrimos de lunes a viernes de 9:00 a 19:00."
}

Listar conocimiento

GET /knowledge/

---

# Sistema RAG

El sistema utiliza Retrieval Augmented Generation.

Proceso:

1 usuario pregunta
2 se normaliza y tokeniza la consulta
3 se puntúan knowledge items por coincidencia de tokens
4 se recupera conocimiento relevante (top_k)
5 se construye prompt
6 el modelo genera respuesta

---

# Estado actual del proyecto

Backend funcional
RAG léxico activo
Base de conocimiento
Historial de conversaciones
Chat AI operativo

---

# Próximos pasos

1 Web chat widget
2 multi-tenant architecture
3 panel admin
4 integración WhatsApp
5 base vectorial pgvector

---

# Licencia

Proyecto experimental en desarrollo.