# Atiende24 V1 — Redefinición pragmática como **AI Support Copilot**

## 1) Redefinición final del producto

- **Propuesta de valor (1 frase):**
  Atiende24 V1 es un copiloto de IA que ayuda a agentes de soporte a responder más rápido y con más consistencia, usando solo la base de conocimiento interna y reglas de escalado claras.

- **Usuario objetivo:**
  Team leads y agentes de soporte de equipos pequeños (3–30 agentes) que trabajan por ticket (email/chat/helpdesk) y sufren variabilidad de calidad + backlog.

- **Problema exacto:**
  Los agentes pierden tiempo buscando información dispersa y redactando respuestas repetitivas; eso baja FCR, sube TTR y genera respuestas inconsistentes.

- **Resultado de negocio esperado:**
  Reducir tiempo promedio de respuesta (AHT/TTR) en 20–35% y aumentar FCR en 10–20% en un piloto de 30 días, sin aumentar headcount.

---

## 2) MVP cerrado

### Qué entra en la V1

1. UI mínima para pegar ticket y recibir borrador de respuesta.
2. RAG sobre una base de conocimiento acotada (SOPs, macros, políticas, FAQs).
3. Clasificación binaria: **responder** vs **escalar a humano**.
4. Score de confianza (0–1) con umbral configurable.
5. Trazabilidad mínima: fuentes usadas, motivo de escalado y logs básicos.

### Qué queda fuera explícitamente

- Integraciones nativas con Zendesk/Freshdesk/Salesforce.
- Multicanal (WhatsApp, voz, redes).
- Analytics avanzados y dashboards ejecutivos.
- Multi-tenant, roles complejos, permisos enterprise.
- Fine-tuning, entrenamiento de modelos propios, enrutamiento inteligente multi-LLM.

### Qué hace exactamente el sistema

- Recibe texto del ticket.
- Recupera fragmentos relevantes de conocimiento.
- Genera un **borrador** de respuesta estilo soporte.
- Calcula score de confianza.
- Si score bajo o detecta riesgo/política, recomienda escalado con razón.

### Qué no debe intentar hacer

- No cerrar tickets automáticamente.
- No ejecutar acciones transaccionales (reembolsos, cambios de cuenta).
- No inventar políticas ni responder fuera de la base aprobada.
- No operar como bot customer-facing autónomo.

---

## 3) Casos de uso

### 3 casos principales

1. **Sugerencia de respuesta rápida:** agente pega ticket y obtiene borrador editable + fuentes.
2. **Asistencia de política/SOP:** sugiere el procedimiento correcto según documentación interna.
3. **Guardrail de riesgo:** detecta temas sensibles y obliga escalado con plantilla.

### 5 ejemplos de tickets/preguntas que sí debería resolver

1. “¿Cómo resetear mi contraseña si no me llega el correo?”
2. “¿Cuál es el SLA de respuesta para plan Pro?”
3. “¿Dónde descargo mis facturas de los últimos 3 meses?”
4. “¿Cuánto tarda una devolución estándar?”
5. “¿Qué datos necesito para abrir un caso técnico?”

### 5 ejemplos que deben escalarse a humano

1. “Quiero reembolso excepcional fuera de política.”
2. “Amenaza legal / chargeback / denuncia formal.”
3. “Acceso comprometido y posible fraude.”
4. “Cliente VIP con impacto reputacional alto.”
5. “Incidente no documentado en KB + caída masiva.”

---

## 4) Flujo funcional mínimo end-to-end

1. **Entrada:** agente pega texto del ticket y metadatos mínimos (canal, idioma, prioridad).
2. **Recuperación de conocimiento:** embedding del ticket + top-k chunks de KB aprobada.
3. **Razonamiento/generación:** prompt estricto: responder solo con contexto recuperado; si falta evidencia, declarar incertidumbre.
4. **Clasificación:** reglas + heurística LLM para etiquetar `RESOLVE` o `ESCALATE`.
5. **Scoring de confianza:** combinación simple de señales:
   - similitud promedio de chunks,
   - cobertura de respuesta vs pregunta,
   - presencia de políticas sensibles.
6. **Decisión de escalado:**
   - si score < umbral (ej. 0.72) => `ESCALATE`,
   - si detecta keyword/riesgo => `ESCALATE` forzado.
7. **Salida:**
   - borrador de respuesta,
   - score,
   - fuentes,
   - etiqueta final,
   - “razón de escalado” si aplica.

---

## 5) Arquitectura técnica mínima

- **Frontend:** Streamlit (una sola pantalla interna de agente).
- **Backend:** FastAPI con 2 endpoints principales (`/copilot/respond`, `/kb/ingest`).
- **Base de conocimiento / RAG:** SQLite + tabla de chunks + vector en JSON (sin infraestructura extra).
- **Embeddings:** `text-embedding-3-small` (bajo costo, suficiente para V1).
- **LLM:** `gpt-4o-mini` (rápido y barato para drafting en soporte).
- **Almacenamiento:** SQLite local (`backend/atiende24.db`) + carpeta `data/knowledge`.
- **Logging:** logs estructurados JSON a archivo + request_id.
- **Despliegue:** Docker Compose (backend + frontend) en una VM simple.
- **Autenticación:** solo un password básico por entorno (si demo interna) o sin auth en localhost.

---

## 6) Stack recomendado (decisión cerrada)

1. **Python + FastAPI**: ya alineado con repo actual; curva baja para iterar.
2. **Streamlit**: UI mínima sin frontend framework complejo.
3. **SQLite**: cero fricción operativa para V1.
4. **OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)**: rapidez de implementación y coste controlable.
5. **Docker Compose**: reproducibilidad local y demo en minutos.
6. **pytest (tests mínimos)**: smoke tests de endpoints críticos.

**Por qué este stack:** minimiza decisiones, reduce mantenimiento y permite avanzar en bloques de 60–90 minutos por sesión.

---

## 7) Mini-PRD

### Objetivo
Entregar en 30 días un copiloto interno que sugiera respuestas de soporte con trazabilidad y escalado seguro.

### Contexto
Hay conocimiento operativo disperso y alto coste de respuesta manual en tickets repetitivos.

### Alcance
- Ingesta manual de documentos base (Markdown/CSV/TXT).
- Motor RAG con respuesta sugerida.
- Clasificación resolve/escalate + score de confianza.
- UI interna mínima para uso de agentes.

### No alcance
- Integraciones helpdesk,
- respuestas automáticas al cliente final,
- analítica avanzada,
- capacidades enterprise.

### Usuarios
- Agente de soporte.
- Team lead/supervisor (valida calidad y escalados).

### Funcionalidades
1. Cargar KB.
2. Preguntar sobre ticket.
3. Ver borrador + fuentes + score + decisión.
4. Registrar evento para auditoría básica.

### Riesgos
- KB incompleta/desactualizada.
- Prompt drift (respuestas demasiado largas o ambiguas).
- Falsa sensación de seguridad por score mal calibrado.

### Métricas de éxito (pilot)
- % tickets con borrador útil (>70%).
- Reducción del tiempo de primera respuesta.
- Tasa de escalado correcta (sin sobreescalar >40%).
- CSAT interno de agentes sobre utilidad (>4/5).

---

## 8) Backlog tipo Jira/Notion

### Épica 1: Setup inicial

- **Tarea:** Inicializar entorno local con Docker Compose.
  - Prioridad: Alta
  - Esfuerzo: S
  - Dependencias: ninguna
- **Tarea:** Configurar `.env.example` y carga de configuración central.
  - Prioridad: Alta
  - Esfuerzo: S
  - Dependencias: entorno base
- **Tarea:** Endpoint healthcheck y estructura base API.
  - Prioridad: Alta
  - Esfuerzo: S
  - Dependencias: FastAPI boot

### Épica 2: Ingesta de conocimiento

- **Tarea:** Definir esquema de documento/chunk/metadatos.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: DB base
- **Tarea:** Script de ingesta (`md/txt/csv`) con chunking simple.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: esquema KB
- **Tarea:** Generar y persistir embeddings por chunk.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: ingesta

### Épica 3: Motor de respuesta

- **Tarea:** Implementar retrieval top-k por similitud coseno.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: embeddings listos
- **Tarea:** Prompt de respuesta con guardrails “solo evidencia”.
  - Prioridad: Alta
  - Esfuerzo: S
  - Dependencias: retrieval
- **Tarea:** Endpoint `/copilot/respond`.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: prompt + retrieval

### Épica 4: Clasificación y escalado

- **Tarea:** Definir taxonomía de riesgo (refund legal/fraud/security/VIP).
  - Prioridad: Alta
  - Esfuerzo: S
  - Dependencias: ninguna
- **Tarea:** Regla de decisión (`RESOLVE`/`ESCALATE`) + umbral configurable.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: scoring base
- **Tarea:** Salida con “motivo de escalado” y recomendación de siguiente acción.
  - Prioridad: Media
  - Esfuerzo: S
  - Dependencias: clasificador

### Épica 5: UI mínima

- **Tarea:** Pantalla única Streamlit (input ticket + output).
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: endpoint respond
- **Tarea:** Visualizar fuentes recuperadas y score.
  - Prioridad: Media
  - Esfuerzo: S
  - Dependencias: contrato API
- **Tarea:** Botón “copiar borrador” y etiqueta de estado.
  - Prioridad: Media
  - Esfuerzo: S
  - Dependencias: UI base

### Épica 6: Demo y validación

- **Tarea:** Dataset de 30 tickets reales anonimizados.
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: ninguna
- **Tarea:** Script de evaluación rápida (útil/no útil, escalado correcto).
  - Prioridad: Alta
  - Esfuerzo: M
  - Dependencias: motor estable
- **Tarea:** Checklist de demo + guion de venta interna.
  - Prioridad: Media
  - Esfuerzo: S
  - Dependencias: UI funcional

---

## 9) Plan de 30 días

### Semana 1
- **Objetivo:** base técnica funcionando end-to-end mínima.
- **Entregables:** backend corriendo, healthcheck, ingesta 1 documento, consulta simple.
- **Tareas críticas:** config, DB, chunking, primer retrieval.
- **Riesgo principal:** atascarse en arquitectura prematura.

### Semana 2
- **Objetivo:** respuestas útiles con fuentes.
- **Entregables:** endpoint `/copilot/respond` estable + prompt v1 + top-k afinado.
- **Tareas críticas:** calidad de chunks, control de alucinaciones, formato de salida.
- **Riesgo principal:** KB de baja calidad.

### Semana 3
- **Objetivo:** clasificación y escalado confiable.
- **Entregables:** score + reglas de riesgo + decisión final reproducible.
- **Tareas críticas:** umbral inicial y casos límite.
- **Riesgo principal:** exceso de falsos positivos de escalado.

### Semana 4
- **Objetivo:** demo usable y validación con tickets reales.
- **Entregables:** Streamlit UI, test rápido, métricas de piloto.
- **Tareas críticas:** UX mínima, estabilidad, narrativa de valor.
- **Riesgo principal:** sobrecargar la demo con features extra.

---

## 10) Estructura inicial del repositorio (pequeña y realista)

```text
Atiende24/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ services/
│  │  └─ main.py
│  ├─ ingestion/
│  ├─ prompts/
│  └─ tests/
├─ frontend/
│  └─ app.py
├─ docs/
├─ data/
│  └─ knowledge/
├─ README.md
├─ .env.example
└─ docker-compose.yml
```

---

## 11) Archivos iniciales sugeridos

- `README.md`
- `.env.example`
- `docker-compose.yml`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/api/copilot.py`
- `backend/app/api/knowledge.py`
- `backend/app/schemas/copilot.py`
- `backend/app/schemas/knowledge.py`
- `backend/app/services/rag_service.py`
- `backend/app/services/classifier.py`
- `backend/app/services/scoring.py`
- `backend/app/services/ai_service.py`
- `backend/app/db/database.py`
- `backend/app/db/models.py`
- `backend/ingestion/load_kb.py`
- `backend/prompts/answer_prompt.txt`
- `backend/prompts/classify_prompt.txt`
- `frontend/app.py`
- `backend/tests/test_health.py`
- `backend/tests/test_copilot_response.py`
- `docs/mvp-prd.md`

---

## 12) README inicial (borrador corto)

### Atiende24
Atiende24 V1 es un **AI Support Copilot** interno para equipos de soporte. No responde directo al cliente final: propone borradores para agentes, con fuentes y decisión de escalado.

### Qué hace V1
- Sugerir respuestas a tickets usando KB interna.
- Mostrar fuentes recuperadas.
- Calcular confianza y recomendar `RESOLVE` o `ESCALATE`.

### Stack
- FastAPI + Python
- Streamlit
- SQLite
- OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)
- Docker Compose

### Ejecutar local
1. Copiar `.env.example` a `.env` y añadir API key.
2. `docker compose up --build`
3. API en `http://localhost:8000/docs`
4. UI en `http://localhost:8501`

### Estructura
- `backend/`: API + RAG + clasificación.
- `frontend/`: interfaz mínima de agente.
- `data/knowledge/`: documentos fuente.
- `docs/`: PRD, decisiones y plan.

### Roadmap corto
1. V1 cerrada (copilot interno con escalado).
2. Piloto con 30 tickets reales.
3. Ajuste de umbral y calidad de KB.

---

## 13) Primeras 10 tareas de implementación (mañana mismo)

1. Crear `.env.example` con variables mínimas.
2. Limpiar README al enfoque “AI Support Copilot”.
3. Crear endpoint `GET /health`.
4. Definir esquema DB para `knowledge_chunks`.
5. Implementar script de chunking para `md/txt/csv`.
6. Generar embeddings y guardarlos en SQLite.
7. Implementar retrieval top-k.
8. Diseñar prompt v1 con formato de salida fijo.
9. Crear endpoint `POST /copilot/respond` con fuentes + score.
10. Construir UI Streamlit de una sola pantalla.

---

## 14) Crítica dura (sin filtro)

1. **Tu riesgo #1 es scope creep**, no tecnología.
   Si metes integraciones o “feature bonita”, no llegas.

2. **No necesitas producto SaaS ahora.**
   Necesitas prueba de valor operativa con un equipo real y tickets reales.

3. **El mayor cuello de botella será la KB**, no el modelo.
   Sin documentos limpios y actualizados, el copiloto fallará aunque uses mejor LLM.

4. **No persigas precisión perfecta en V1.**
   Tu objetivo es “borrador útil + buen escalado”, no automatización total.

5. **Tu plan original aún puede ser grande.**
   Si te quedas corto de tiempo, reduce a:
   - 1 canal de entrada manual (copiar/pegar ticket),
   - 1 tipo de documento (solo markdown),
   - 1 idioma,
   - solo 4 categorías de escalado.

6. **Regla brutal de priorización:**
   Si una tarea no mejora directamente “tiempo de respuesta” o “calidad consistente”, se elimina.

---

## Cierre solicitado

### 1) Versión final resumida del producto
Atiende24 V1 = copiloto interno para agentes de soporte que genera borradores con fuentes y decide cuándo escalar, para bajar tiempos de respuesta y subir consistencia operativa.

### 2) Stack final recomendado
FastAPI + Streamlit + SQLite + OpenAI (`gpt-4o-mini` + `text-embedding-3-small`) + Docker Compose + pytest básico.

### 3) Primer sprint recomendado
Semana 1 enfocada en base funcional: healthcheck, ingesta KB mínima, embeddings, retrieval y primer endpoint de respuesta con fuentes (sin UI bonita).
