# Arquitectura del sistema Atiende24

Este documento describe la arquitectura técnica del sistema.

---

# Diagrama general

Usuario
   │
   ▼
Web Widget / API Client
   │
   ▼
FastAPI Backend
   │
   ├── Chat API
   ├── Knowledge API
   │
   ▼
RAG Engine
   │
   ├── Embedding Generation
   ├── Semantic Search
   │
   ▼
OpenAI API

---

# Componentes

## API Layer

FastAPI expone los endpoints principales

/chat/message
/knowledge

Responsabilidades

gestión de peticiones
validación
orquestación

---

## RAG Engine

Sistema de recuperación de conocimiento.

Pasos:

1 generar embedding pregunta
2 comparar con embeddings
3 ordenar por similitud
4 devolver top_k
5 construir prompt

---

## Base de datos

SQLite

Tablas

conversations
messages
knowledge_items

---

## Embeddings

Modelo

text-embedding-3-small

Cada knowledge item se convierte en vector semántico.

Se almacenan serializados en JSON.

---

## Modelo LLM

Modelo actual

gpt-4o-mini

Responsabilidades

generar respuestas
mantener conversación
usar contexto

---

# Flujo de una pregunta

Usuario envía pregunta
       │
       ▼
API recibe mensaje
       │
       ▼
se guarda mensaje
       │
       ▼
generar embedding
       │
       ▼
buscar conocimiento relevante
       │
       ▼
crear prompt
       │
       ▼
OpenAI genera respuesta
       │
       ▼
guardar respuesta
       │
       ▼
enviar respuesta al usuario

---

# Evolución futura

vector database
multi tenant
panel admin
integraciones