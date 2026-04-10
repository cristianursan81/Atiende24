# Atiende24

AI Support Copilot for Internal Support Teams

Atiende24 V1 is an internal AI Support Copilot designed to help support agents respond faster and more consistently using an approved knowledge base and simple escalation rules.

It is **not** a public-facing chatbot.  
It is a tool for internal support operations.

---

## What Atiende24 V1 does

Atiende24 helps support teams:

- analyze incoming tickets
- retrieve relevant knowledge base content
- draft grounded reply suggestions
- classify the case
- decide whether the case should be escalated to a human

The goal is to reduce response time, improve consistency, and lower agent cognitive load.

---

## Core use case

An agent pastes a support ticket into the system.

Atiende24 then:

1. retrieves relevant internal knowledge
2. classifies the case
3. estimates confidence
4. returns one of two outcomes:
   - **suggested reply**
   - **escalate to human**, with reason

---

## What V1 is not

Atiende24 V1 does **not** include:

- public chatbot
- WhatsApp
- email delivery
- voice
- CRM integrations
- multi-tenant support
- admin panel
- advanced analytics
- autonomous customer replies
- transactional actions on customer accounts

---

## Architecture

Atiende24 uses a lightweight API-based architecture.

Support Agent UI / Internal Demo UI
        │
        ▼
FastAPI Backend
        │
        ├── Analyze Ticket Endpoint
        ├── Knowledge Base Access
        │
        ▼
SQLite Database
        │
        ├── Knowledge metadata
        ├── Logs
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

## Tech stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- OpenAI API
- python-dotenv

### AI
- Chat model: `gpt-4o-mini`
- Embedding model: `text-embedding-3-small`

### Optional UI
- Streamlit for internal demo

---

## Current project structure

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
│   │       ├── embedding_service.py
│   │       └── semantic_rag_service.py
│   │
│   ├── .env
│   ├── atiende24.db
│   ├── requirements.txt
│   └── run.py

---

## Environment variables

File:

`backend/.env`

Content:

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```
