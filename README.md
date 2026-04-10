# Atiende24

## AI Support Copilot for Internal Support Teams

Atiende24 V1 es un copiloto interno para equipos de soporte.
Su objetivo es ayudar a agentes a responder con mayor velocidad y consistencia usando una base de conocimiento aprobada.

---

## Qué es Atiende24 V1

Atiende24 V1 es una herramienta interna de asistencia para operaciones de soporte.
No reemplaza al agente: propone borradores, aporta contexto y recomienda escalado cuando detecta baja confianza o riesgo.

---

## Qué hace hoy

- recibe el texto de un ticket
- busca contexto relevante en la base de conocimiento
- genera un borrador de respuesta basado en evidencia recuperada
- registra conversación y mensajes
- permite administrar conocimiento desde API

---

## Qué no hace en V1

- no ejecuta acciones transaccionales sobre cuentas
- no toma decisiones finales sin revisión humana
- no incluye automatizaciones externas de alto alcance
- no incorpora capacidades enterprise avanzadas

---

## Flujo de uso interno (agente)

1. el agente pega una consulta o ticket en el sistema
2. el backend recupera contenido relevante de la base de conocimiento
3. el motor de IA redacta una respuesta sugerida
4. el agente revisa, ajusta y envía por su herramienta habitual
5. si la confianza es baja o el caso es sensible, se deriva a escalado

---

## Arquitectura alineada a V1

```text
Agent/Internal UI
      │
      ▼
FastAPI Backend
      ├── /chat/message
      ├── /knowledge/
      ▼
SQLite Database
      ├── conversations
      ├── messages
      └── knowledge_items
      ▼
RAG Service
      ├── embeddings
      └── similarity retrieval
      ▼
OpenAI Models
```

---

## Stack actual

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- python-dotenv

### AI
- OpenAI Chat Model: `gpt-4o-mini`
- OpenAI Embedding Model: `text-embedding-3-small`

### Dependencias principales
- numpy
- pytest
- tqdm

---

## Estado actual del proyecto

- API funcional con endpoints de chat y conocimiento
- modelo de datos para conversaciones, mensajes y conocimiento
- servicio RAG base implementado
- integración con OpenAI para embeddings y generación
- documentación técnica inicial en `docs/`

---

## Próximo sprint técnico (realista)

Objetivo: consolidar el flujo de copiloto interno con trazabilidad mínima.

1. unificar endpoint de respuesta tipo copilot con fuentes recuperadas
2. incorporar score simple de confianza y razón de escalado
3. mejorar chunking/ingesta para calidad de recuperación
4. agregar smoke tests de API (`health`, `chat`, `knowledge`)
5. preparar demo interna de punta a punta con 10 tickets de prueba

---

## Ejecución local

### 1) Variables de entorno
Crear `backend/.env` con:

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Levantar backend

```bash
cd backend
python run.py
```

API docs:
- `http://localhost:8000/docs`

---

## Estructura actual del repositorio

```text
Atiende24/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   └── services/
│   ├── run.py
│   └── requirements.txt
├── docs/
├── requirements.txt
└── README.md
```
