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
   ├── Normalización/tokenización
   ├── Scoring léxico por tokens
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

1 normalizar/tokenizar pregunta
2 tokenizar knowledge items
3 puntuar coincidencias
4 ordenar por score y devolver top_k
5 construir prompt

---

## Base de datos

SQLite

Tablas

conversations
messages
knowledge_items

---

## Recuperación de conocimiento

El MVP actual usa recuperación léxica basada en tokens y stopwords en español.

No almacena embeddings ni vectores en base de datos.

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
normalizar y tokenizar consulta
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