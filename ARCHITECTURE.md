# Arquitectura del sistema ChatGenie (anteriormente Atiende24)

Este documento describe la arquitectura técnica del sistema completo, incluyendo la nueva integración con LinkEvolution.

---

# Diagrama general

Cliente (LinkEvolution Website)
   │
   ▼
ChatGenie Widget (JavaScript)
   │
   ├── Voice Recognition API
   ├── Text-to-Speech API  
   ├── LocalStorage
   │
   ▼
FastAPI Backend (ChatGenie API)
   │
   ├── Chat API (/api/chat)
   ├── Knowledge API (/api/knowledge)
   ├── Business API (/api/business)
   ├── SME Services APIs
   │   ├── Leads API (/api/leads)
   │   ├── Analytics API (/api/analytics)
   │   ├── Templates API (/api/templates)
   │   ├── CRM API (/api/crm)
   │   └── Sessions API (/api/sessions)
   │
   ▼
AI Services Layer
   │
   ├── RAG Engine
   │   ├── Embedding Generation
   │   ├── Semantic Search
   │   └── Vector Database
   ├── Language Models
   │   └── OpenAI API
   └── Business Intelligence
       ├── Lead Scoring
       ├── Intent Recognition
       └── Analytics Engine
   │
   ▼
Data Layer
   │
   ├── SQLite Database
   │   ├── Core Tables (users, businesses, chats)
   │   └── SME Tables (leads, analytics, templates, etc.)
   └── File Storage (knowledge base, templates)

---

# Componentes

## Frontend Layer - ChatGenie Widget

### Core Widget (chat-widget.js)
- **Responsabilidades**: Interfaz de usuario, gestión de estado local, comunicación con API
- **Características**: Arrastrable, temas claros/oscuros, reconocimiento de voz, notificaciones
- **Tecnologías**: Vanilla JavaScript, CSS3, HTML5 APIs

### LinkEvolution Integration
- **Archivos específicos**: 
  - `linkevolution-embed.js` - Widget personalizado
  - `linkevolution-embed.html` - Demo y documentación
  - `chatgenie-widget.php` - Integración PHP/WordPress
- **Características**: Branding LinkEvolution, idioma español, quick actions transformación digital
- **Configuración**: Horarios comerciales Madrid, captación leads especializada

## API Layer

### Chat Management
- **Endpoint**: `/api/chat`
- **Responsabilidades**: Procesamiento de mensajes, gestión de conversaciones, integración IA
- **Funciones**: Detección de intención, generación de respuestas, escalado humano

### Business Intelligence
- **Endpoints**: `/api/leads`, `/api/analytics`, `/api/templates`
- **Responsabilidades**: Captación y gestión de leads, análisis de conversaciones, templates de industria
- **Funciones**: Lead scoring, segmentación, reporting automático

### Session Management  
- **Endpoint**: `/api/sessions`
- **Responsabilidades**: Gestión de sesiones de chat, tracking de usuarios, métricas de engagement
- **Funciones**: Persistencia de conversaciones, analytics de sesión, datos de comportamiento

### Knowledge Management
- **Endpoint**: `/api/knowledge`
- **Responsabilidades**: Gestión de base de conocimiento, búsqueda semántica
- **Funciones**: Upload de documentos, indexado, recuperación contextual

## AI Services Layer

### RAG Engine
- **Responsabilidades**: Recuperación de información contextual para respuestas precisas
- **Componentes**: 
  - Generación de embeddings (OpenAI text-embedding-3-small)
  - Búsqueda semántica en base de conocimiento
  - Ranking y filtrado de resultados relevantes
- **Optimizaciones**: Caché de embeddings, indexado vectorial, chunking inteligente

### Intent Recognition & Lead Scoring
- **Responsabilidades**: Identificación automática de intenciones de compra y scoring de leads
- **Algoritmos**: NLP para análisis de sentimiento, clasificación de queries, detección de urgencia
- **Integración**: Triggers automáticos para captación de leads, routing inteligente

### Business Intelligence Engine
- **Responsabilidades**: Analytics avanzados, insights de conversaciones, predicciones de comportamiento
- **Métricas**: Conversion rates, lead quality, satisfaction scores, topic modeling
- **Outputs**: Dashboards ejecutivos, reportes automáticos, alertas proactivas

## Data Layer

### Core Database Schema
```sql
-- Tablas principales
businesses (id, name, config, created_at)
users (id, business_id, email, role, created_at)
conversations (id, business_id, user_id, status, created_at)
messages (id, conversation_id, content, type, created_at)
```

### SME Business Schema  
```sql
-- Extensiones SME
leads (id, business_id, contact_info, source, score, status)
analytics (id, business_id, metrics, period, created_at)
templates (id, business_id, industry, content, variables)
crm_integrations (id, business_id, provider, config, status)
business_hours (id, business_id, timezone, schedule, holidays)
product_catalog (id, business_id, name, description, price)
chat_sessions (id, business_id, session_data, duration, end_reason)
settings (id, business_id, key, value, type)
```

### File Storage
- **Knowledge Base**: Documentos de empresa, FAQs, procedimientos
- **Templates**: Plantillas de respuesta por industria y contexto  
- **Assets**: Logos, imágenes, archivos multimedia para branding
- **Backups**: Respaldos automáticos de conversaciones y datos críticos

---

# Flujos de Trabajo

## Flujo de Conversación Típica

1. **Inicialización Widget**
   ```
   Usuario visita linkevolution.eu → Widget se carga → Configuración LinkEvolution aplicada
   ```

2. **Inicio de Sesión**
   ```
   Usuario hace clic → Sesión creada en DB → Greeting personalizado mostrado
   ```

3. **Conversación Activa**
   ```
   Mensaje usuario → API /chat → RAG Engine → OpenAI → Respuesta + Lead Scoring
   ```

4. **Captación de Lead**
   ```
   Trigger detectado → Formulario lead → Datos guardados → Notificación CRM → Follow-up automático
   ```

## Flujo de Captación de Leads LinkEvolution

1. **Detección de Intención**
   - Keywords: "presupuesto", "consultoría", "transformación digital", "automatización"
   - Context analysis: Empresa, proyecto, urgencia, budget signals

2. **Lead Qualification**  
   - Scoring automático basado en conversation depth, company size, urgency indicators
   - Clasificación: Hot (immmediate follow-up), Warm (nurturing sequence), Cold (newsletter)

3. **Data Enrichment**
   - Información capturada: Nombre, email, empresa, teléfono, proyecto específico
   - Validación automática: Email verification, empresa lookup, domain analysis

4. **CRM Integration**
   - Envío automático a sistema CRM de LinkEvolution
   - Asignación de lead owner basado en tipo de proyecto
   - Trigger de workflow de seguimiento personalizado

---

# Configuración de Producción

## Requisitos Técnicos
- **Servidor**: Python 3.12+, FastAPI, SQLAlchemy
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción recomendada)
- **SSL**: Certificados válidos para HTTPS obligatorio
- **CDN**: Recomendado para distribución de widget JavaScript

## Variables de Entorno
```env
# Core Configuration  
CHATGENIE_ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/chatgenie
OPENAI_API_KEY=sk-xxx

# LinkEvolution Specific
LINKEVO_BUSINESS_ID=1
LINKEVO_API_KEY=xxx
LINKEVO_WEBHOOK_URL=https://crm.linkevolution.eu/webhook
LINKEVO_WHATSAPP_TOKEN=xxx
```

## Monitoreo y Métricas
- **Health Checks**: `/health`, `/readiness`  
- **Metrics**: Prometheus endpoints para grafana dashboards
- **Logging**: Estructurado JSON con correlation IDs
- **Alerting**: PagerDuty integration para incidencias críticas

---

# Seguridad e Integraciones

## Seguridad
- **Autenticación**: JWT tokens con expiración, API keys por business
- **Autorización**: RBAC con permisos granulares por endpoint  
- **Rate Limiting**: Por IP, por API key, por business
- **Data Protection**: GDPR compliant, encriptación at-rest y in-transit

## Integraciones Existentes
- **OpenAI**: GPT-4 para generación de respuestas
- **WhatsApp Business**: LinkEvolution integration ready
- **Google Analytics**: Event tracking para conversion funnels
- **Email Services**: SMTP/SendGrid para notifications

## Integraciones Planificadas
- **Slack**: Notificaciones internas para equipo LinkEvolution  
- **HubSpot/Salesforce**: CRM bidirectional sync
- **Zapier**: Workflow automation triggers
- **Microsoft Teams**: Enterprise chat integration

---

# Roadmap Técnico

## Q1 2024
- ✅ Widget base con IA conversacional
- ✅ LinkEvolution integration completa
- ✅ Sistema SME de leads y analytics
- 🔄 Deployment en producción linkevolution.eu

## Q2 2024  
- 📋 Multi-language support (English, Portuguese)
- 📋 Advanced analytics dashboard
- 📋 A/B testing framework para optimization
- 📋 Mobile app complement (opcional)

## Q3 2024
- 📋 Voice-first interactions (complete voice UI)
- 📋 Video chat integration  
- 📋 WhatsApp Business API full integration
- 📋 Enterprise SSO (SAML, OAuth2)

## Q4 2024
- 📋 AI-powered appointment scheduling
- 📋 Multi-channel unified inbox
- 📋 Predictive lead scoring ML models
- 📋 White-label platform for other agencies

---

Este sistema representa una evolución completa desde un simple chat widget a una plataforma integral de customer engagement especializada para empresas de transformación digital como LinkEvolution.

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