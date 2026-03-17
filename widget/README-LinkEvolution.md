# ChatGenie - Integración LinkEvolution

## 🚀 Asistente de IA para Transformación Digital

ChatGenie es un widget de chat inteligente diseñado específicamente para **LinkEvolution**, especializado en servicios de transformación digital, automatización de procesos y consultoría empresarial.

### ✨ Características Principales

- **🧠 IA Avanzada**: Respuestas inteligentes especializadas en transformación digital
- **🎤 Control por Voz**: Reconocimiento de voz en español
- **🌙 Tema Adaptativo**: Modo oscuro/claro automático
- **📱 Responsive**: Diseño optimizado para móviles y escritorio
- **🎯 Captación de Leads**: Sistema automático de generación de leads
- **⏰ Horario Comercial**: Gestión automática de horarios de atención
- **🇪🇸 Localización**: Completamente en español para el mercado español

### 🛠️ Instalación Rápida

#### Opción 1: Integración HTML Directa

```html
<!-- Incluir en el <head> de tu página -->
<script>
window.ChatGenieConfig = {
    businessId: '1',
    apiKey: 'your-api-key',
    apiBaseUrl: 'https://tu-dominio.com',
    branding: {
        businessName: 'LinkEvolution',
        primaryColor: '#667eea',
        secondaryColor: '#764ba2',
        accentColor: '#FFD700',
        logo: 'https://www.linkevolution.eu/images/logo.png'
    },
    template: 'digital_transformation',
    language: 'es-ES',
    greeting: '¡Hola! Soy el asistente de LinkEvolution. ¿Cómo puedo ayudarte con tu transformación digital?',
    quickActions: [
        {text: '🚀 Transformación Digital', message: 'Quiero información sobre transformación digital'},
        {text: '⚡ Automatización', message: 'Me interesa automatizar procesos'},
        {text: '📊 Gestión de Flujos', message: 'Necesito ayuda con gestión de flujos de trabajo'},
        {text: '💼 Consultoría', message: 'Quiero una consultoría personalizada'},
        {text: '📞 Contactar', message: 'Quiero hablar con un consultor'},
        {text: '💰 Presupuesto', message: 'Necesito un presupuesto'}
    ]
};
</script>

<!-- Cargar el widget -->
<script src="https://tu-dominio.com/widget/linkevolution-embed.js" async></script>
```

#### Opción 2: Integración WordPress/PHP

```php
<?php include 'chatgenie-widget.php'; ?>
```

### ⚙️ Configuración Personalizada

#### Branding de LinkEvolution
```javascript
branding: {
    businessName: 'LinkEvolution',
    primaryColor: '#667eea',    // Azul corporativo
    secondaryColor: '#764ba2',  // Púrpura complementario
    accentColor: '#FFD700',     // Dorado para destacar
    logo: 'https://www.linkevolution.eu/images/logo.png'
}
```

#### Acciones Rápidas Especializadas
```javascript
quickActions: [
    {text: '🚀 Transformación Digital', message: 'Quiero información sobre transformación digital', action: 'digital_transformation'},
    {text: '⚡ Automatización', message: 'Me interesa automatizar procesos', action: 'automation'},
    {text: '📊 Gestión de Flujos', message: 'Necesito ayuda con gestión de flujos de trabajo', action: 'workflow_management'},
    {text: '💼 Consultoría', message: 'Quiero una consultoría personalizada', action: 'consultation'},
    {text: '📞 Contactar', message: 'Quiero hablar con un consultor', action: 'contact'},
    {text: '💰 Presupuesto', message: 'Necesito un presupuesto', action: 'quote'}
]
```

#### Horario Comercial Madrid
```javascript
businessHours: {
    timezone: 'Europe/Madrid',
    monday: {open: '09:00', close: '19:00'},
    tuesday: {open: '09:00', close: '19:00'},
    wednesday: {open: '09:00', close: '19:00'},
    thursday: {open: '09:00', close: '19:00'},
    friday: {open: '09:00', close: '18:00'},
    afterHoursMessage: 'Estamos fuera del horario de atención. Déjanos tu consulta y te contactaremos pronto. También puedes llamarnos al +34 647 027 418.'
}
```

#### Captación de Leads Inteligente
```javascript
leadCapture: {
    enabled: true,
    triggers: [
        'presupuesto', 'precio', 'coste', 'consultoría', 'reunión', 'contactar',
        'transformación digital', 'automatización', 'contacto', 'información',
        'demo', 'prueba', 'análisis', 'audit', 'evaluación'
    ]
}
```

### 📊 Funcionalidades Empresariales

#### 🎯 Generación de Leads
- **Detección Automática**: Identifica consultas de alta intención
- **Formulario Inteligente**: Captura contactos de manera natural
- **Segmentación**: Clasifica leads por tipo de servicio
- **Integración CRM**: Envía leads directamente a tu sistema

#### 📈 Analytics y Reporting
- **Conversaciones**: Número de chats iniciados
- **Leads Generados**: Contactos obtenidos por período
- **Temas Populares**: Servicios más consultados
- **Horarios de Mayor Actividad**: Optimización de atención

#### 🤖 IA Especializada
- **Base de Conocimiento**: Entrenada en transformación digital
- **Respuestas Contextuales**: Adapta respuestas según el servicio
- **Escalado Inteligente**: Deriva a humanos cuando es necesario

### 🔧 Configuración Avanzada

#### Variables de Entorno
```env
CHATGENIE_BUSINESS_ID=1
CHATGENIE_API_KEY=your-api-key
CHATGENIE_API_URL=https://tu-dominio.com
CHATGENIE_ENVIRONMENT=production
```

#### Personalización CSS
```css
/* Personalizar colores del widget */
#chatgenie-container {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --accent-color: #FFD700;
}
```

### 📱 Responsive Design

El widget está optimizado para:
- **Desktop**: Experiencia completa con arrastrar y soltar
- **Tablet**: Interfaz adaptada para pantallas medianas
- **Móvil**: Versión optimizada para pantallas pequeñas

### 🔒 Seguridad y Privacidad

- **HTTPS**: Todas las comunicaciones encrypted
- **RGPD**: Cumple con regulaciones de privacidad europeas
- **Datos Locales**: Información sensible almacenada localmente
- **API Segura**: Autenticación con tokens JWT

### 📞 Integración WhatsApp

```javascript
// Configuración WhatsApp Business
whatsapp: {
    enabled: true,
    number: '+34647027418',
    message: 'Hola LinkEvolution, me interesa información sobre transformación digital'
}
```

### 🚀 Deployment

#### 1. Configuración del Servidor
```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env

# Iniciar servidor
npm start
```

#### 2. Configuración DNS
```
# Agregar registros CNAME
chat.linkevolution.eu CNAME tu-servidor-chatgenie.com
api.linkevolution.eu CNAME tu-api-chatgenie.com
```

#### 3. SSL Certificate
```bash
# Certbot para HTTPS
certbot --nginx -d chat.linkevolution.eu -d api.linkevolution.eu
```

### 📊 Métricas de Rendimiento

#### KPIs Principales
- **Conversion Rate**: % de visitantes que inician chat
- **Lead Generation Rate**: % de chats que generan leads
- **Response Time**: Tiempo promedio de primera respuesta
- **Customer Satisfaction**: Rating promedio de satisfacción

#### Objetivos LinkEvolution
- **🎯 Target Conversion Rate**: 3-5%
- **📈 Lead Generation Goal**: 20-30 leads/mes
- **⚡ Response Time Goal**: <2 segundos
- **⭐ Satisfaction Goal**: >4.5/5

### 🛠️ Troubleshooting

#### Problemas Comunes

**Widget no aparece**
```javascript
// Verificar configuración
console.log(window.ChatGenieConfig);

// Verificar carga del script
console.log('ChatGenie script loaded:', !!window.ChatGenie);
```

**API no responde**
```bash
# Verificar conectividad
curl -X GET "https://tu-dominio.com/api/health"

# Verificar logs del servidor
tail -f /var/log/chatgenie/app.log
```

### 📞 Soporte

Para soporte técnico:
- **Email**: soporte@linkevolution.eu
- **WhatsApp**: +34 647 027 418
- **Horario**: L-V 9:00-19:00 (CET)

### 📄 Licencia

© 2024 LinkEvolution - ChatGenie Widget
Uso exclusivo para LinkEvolution y clientes autorizados.

---

### 🎨 Demo en Vivo

Visita [linkevolution-embed.html](./linkevolution-embed.html) para ver el widget en acción con la configuración completa de LinkEvolution.

### 🔄 Updates

- **v2.0.0**: Integración LinkEvolution completa
- **v1.5.0**: Captación de leads automática
- **v1.0.0**: Widget base con IA