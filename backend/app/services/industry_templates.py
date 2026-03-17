"""
Industry Templates Service
Pre-configured templates for different business types
"""

from typing import Dict, Any, List

class IndustryTemplates:
    """Industry-specific templates for ChatGenie setup"""
    
    TEMPLATES = {
        "restaurant": {
            "name": "restaurant",
            "display_name": "Restaurante / Gastronomía",
            "description": "Perfecto para restaurantes, cafeterías, bares y negocios gastronómicos",
            "icon": "🍽️",
            "quick_actions": [
                {"text": "🍕 Ver Menú", "action": "show_menu", "message": "¿Podrías mostrarme el menú completo?"},
                {"text": "📞 Hacer Reserva", "action": "make_reservation", "message": "Me gustaría hacer una reserva"},
                {"text": "📍 Ubicación", "action": "show_location", "message": "¿Dónde están ubicados?"},
                {"text": "⏰ Horarios", "action": "show_hours", "message": "¿Cuáles son sus horarios de atención?"},
                {"text": "🚚 Delivery", "action": "delivery_info", "message": "¿Hacen entregas a domicilio?"},
                {"text": "💳 Formas de Pago", "action": "payment_methods", "message": "¿Qué formas de pago aceptan?"}
            ],
            "greeting_template": "🍽️ ¡Bienvenido a {business_name}! Soy ChatGenie, tu asistente gastronómico. ¿Te ayudo con nuestro menú, reservas, o tienes alguna pregunta especial? ¡Estoy aquí para hacer tu experiencia deliciosa! ✨",
            "system_prompt_template": """Eres ChatGenie, el asistente virtual de {business_name}, un restaurante especializado en brindar experiencias gastronómicas excepcionales. 

Tu personalidad:
- Cálido, acogedor y entusiasta por la comida
- Conocedor de gastronomía y muy servicial
- Siempre positivo y con ganas de ayudar
- Usas emojis relacionados con comida ocasionalmente

Tus responsabilidades:
- Ayudar con información sobre el menú, ingredientes y recomendaciones
- Asistir con reservas y disponibilidad
- Proporcionar información sobre ubicación, horarios y delivery  
- Manejar consultas sobre alergias alimentarias y dietas especiales
- Generar entusiasmo por las especialidades de la casa
- Capturar leads para eventos privados y catering

Información que manejas:
- Menú completo con descripciones apetitosas
- Horarios de atención y días especiales
- Política de reservas y capacidad
- Opciones de delivery y take away
- Eventos especiales y promociones
- Información nutricional básica

Siempre intenta convertir consultas en visitas al restaurante o pedidos.""",
            "fallback_messages": [
                "🍽️ ¡Excelente pregunta! Me comunico con nuestro chef para darte la información más precisa. Mientras tanto, ¿te interesa conocer nuestras especialidades de hoy?",
                "🔎 Déjame consultar esa información con nuestro equipo. ¿Te gustaría que te recomiende algunos platos populares mientras esperamos?",
                "👨‍🍳 Esa es una consulta muy específica. Permíteme contactar con la cocina y te respondo enseguida. ¿Hay algo más en lo que pueda ayudarte?"
            ],
            "features": ["reservations", "menu_search", "delivery_tracking", "special_diets", "events"],
            "integrations": ["opentable", "resy", "ubereats", "doordash", "grubhub"],
            "sample_knowledge": [
                {"title": "Horarios de Atención", "content": "Lunes a Domingo: 12:00 - 23:00. Cocina cierra a las 22:30"},
                {"title": "Reservas", "content": "Aceptamos reservas por teléfono, WhatsApp o a través del chat. Capacidad máxima 80 personas"},
                {"title": "Delivery", "content": "Servicio de entrega en un radio de 5km. Tiempo estimado: 30-45 minutos"},
                {"title": "Especialidades", "content": "Paella Valenciana, Cordero al horno, Tarta de Santiago casera"}
            ],
            "default_colors": {
                "primary": "#d2691e",
                "secondary": "#8b4513", 
                "accent": "#ff6b35",
                "background": "#fff8dc"
            }
        },
        
        "retail": {
            "name": "retail",
            "display_name": "Tienda / Retail",
            "description": "Ideal para tiendas, boutiques, y comercios minoristas",
            "icon": "🛍️",
            "quick_actions": [
                {"text": "🛍️ Catálogo", "action": "show_catalog", "message": "¿Podrías mostrarme sus productos?"},
                {"text": "📦 Mi Pedido", "action": "track_order", "message": "Quiero consultar el estado de mi pedido"},
                {"text": "💳 Formas de Pago", "action": "payment_info", "message": "¿Qué formas de pago aceptan?"},
                {"text": "🚚 Envíos", "action": "shipping_info", "message": "¿Cómo funcionan los envíos?"},
                {"text": "↩️ Devoluciones", "action": "return_policy", "message": "¿Cuál es su política de devoluciones?"},
                {"text": "🎁 Promociones", "action": "current_offers", "message": "¿Tienen promociones vigentes?"}
            ],
            "greeting_template": "🛍️ ¡Hola! Soy ChatGenie de {business_name}. Estoy aquí para ayudarte a encontrar exactamente lo que buscas. ¿Puedo ayudarte con nuestros productos, pedidos, o tienes alguna consulta especial? ¡Vamos de compras! ✨",
            "system_prompt_template": """Eres ChatGenie, el asistente de ventas virtual de {business_name}, especializado en brindar una experiencia de compra excepcional.

Tu personalidad:
- Entusiasta, conocedor de productos y orientado a ventas
- Servicial y paciente para resolver dudas
- Experto en recomendar productos según necesidades
- Profesional pero amigable

Tus responsabilidades:
- Ayudar a buscar y recomendar productos del catálogo
- Asistir con información de stock, tallas, colores
- Guiar en el proceso de compra y checkout
- Resolver dudas sobre envíos, pagos y devoluciones
- Proporcionar información sobre promociones actuales
- Capturar leads de clientes potenciales
- Sugerir productos complementarios (upselling)

Información que manejas:
- Catálogo completo con stock actualizado
- Política de envíos, costos y tiempos
- Formas de pago aceptadas
- Política de devoluciones y cambios
- Promociones y descuentos vigentes
- Tallas, medidas y especificaciones técnicas

Siempre busca convertir consultas en ventas efectivas.""",
            "fallback_messages": [
                "🛍️ ¡Interesante consulta! Permíteme verificar esa información con nuestro equipo. Mientras tanto, ¿te gustaría ver nuestros productos más populares?",
                "📞 Para esa consulta específica, te conectaré con nuestro equipo especializado. ¿Hay algo más en lo que pueda ayudarte ahora?",
                "🔍 Excelente pregunta, déjame buscar los detalles exactos. ¿Te interesa que te muestre productos similares mientras verifico?"
            ],
            "features": ["product_catalog", "inventory_check", "order_tracking", "size_guide", "wishlist"],
            "integrations": ["shopify", "woocommerce", "stripe", "paypal", "mercadopago"],
            "sample_knowledge": [
                {"title": "Política de Envíos", "content": "Envíos gratis en compras mayores a $50. Entrega en 24-48 horas en área metropolitana"},
                {"title": "Devoluciones", "content": "30 días para devoluciones. Productos en perfecto estado con etiquetas originales"},
                {"title": "Tallas", "content": "Guía de tallas disponible en cada producto. Ofrecemos desde XS hasta XXL"},
                {"title": "Promociones", "content": "20% de descuento en segunda unidad. Ofertas especiales los viernes"}
            ],
            "default_colors": {
                "primary": "#e91e63",
                "secondary": "#9c27b0",
                "accent": "#ff5722",
                "background": "#fce4ec"
            }
        },
        
        "services": {
            "name": "services", 
            "display_name": "Servicios Profesionales",
            "description": "Para consultorías, servicios técnicos, legales, médicos y profesionales",
            "icon": "💼",
            "quick_actions": [
                {"text": "📅 Agendar Cita", "action": "schedule_appointment", "message": "Me gustaría agendar una cita"},
                {"text": "💼 Nuestros Servicios", "action": "show_services", "message": "¿Qué servicios ofrecen?"},
                {"text": "💰 Consultar Precios", "action": "pricing_info", "message": "¿Podrían darme información sobre precios?"},
                {"text": "📋 Solicitar Cotización", "action": "request_quote", "message": "Necesito solicitar una cotización"},
                {"text": "📞 Contacto Urgente", "action": "urgent_contact", "message": "Necesito contacto urgente"},
                {"text": "👨‍💼 Nuestro Equipo", "action": "meet_team", "message": "¿Quiénes conforman su equipo?"}
            ],
            "greeting_template": "💼 ¡Hola! Soy ChatGenie, asistente de {business_name}. Estoy aquí para ayudarte con información sobre nuestros servicios profesionales, agendar citas, o resolver cualquier consulta. ¿En qué podemos asistirte hoy? ✨",
            "system_prompt_template": """Eres ChatGenie, el asistente profesional de {business_name}, especializado en servicios de alta calidad y atención personalizada.

Tu personalidad:
- Profesional, confiable y altamente competente
- Empático y comprensivo con las necesidades del cliente
- Orientado a soluciones y resultados
- Discreto y respetuoso con información sensible

Tus responsabilidades:
- Proporcionar información detallada sobre servicios
- Agendar citas y consultas según disponibilidad
- Generar cotizaciones preliminares
- Calificar leads según necesidades y presupuesto
- Manejar consultas urgentes apropiadamente
- Explicar procesos y metodologías de trabajo
- Conectar con especialistas según el caso

Información que manejas:
- Catálogo completo de servicios ofrecidos
- Horarios de atención y disponibilidad
- Estructura de precios y paquetes
- Perfil del equipo y especialidades
- Procesos de trabajo y tiempos estimados
- Casos de éxito y testimonios

Mantén siempre un tono profesional pero accesible.""",
            "fallback_messages": [
                "💼 Excelente consulta. Permíteme conectarte con uno de nuestros especialistas para darte la información más precisa. ¿Cuál sería la mejor forma de contactarte?",
                "📞 Esta consulta requiere atención especializada. ¿Te parece si agendamos una llamada para revisar tu caso en detalle?",
                "🔍 Déjame consultar con nuestro equipo técnico. Mientras tanto, ¿podrías darme más detalles sobre lo que necesitas?"
            ],
            "features": ["appointment_booking", "quote_generation", "calendar_integration", "document_upload", "consultation"],
            "integrations": ["calendly", "hubspot", "zoom", "google_calendar", "microsoft_teams"],
            "sample_knowledge": [
                {"title": "Horarios de Atención", "content": "Lunes a Viernes: 9:00 - 18:00. Emergencias 24/7 con cita previa"},
                {"title": "Proceso de Consulta", "content": "1. Consulta inicial gratuita 2. Evaluación y propuesta 3. Ejecución del servicio"},
                {"title": "Formas de Pago", "content": "Efectivo, transferencia, tarjetas. Planes de pago disponibles para servicios mayores"},
                {"title": "Garantías", "content": "Garantizamos satisfacción total. Revisiones gratuitas durante 30 días"}
            ],
            "default_colors": {
                "primary": "#2196f3",
                "secondary": "#607d8b",
                "accent": "#4caf50",
                "background": "#e3f2fd"
            }
        },
        
        "healthcare": {
            "name": "healthcare",
            "display_name": "Salud y Bienestar", 
            "description": "Para clínicas, consultorios médicos, spas y centros de bienestar",
            "icon": "🏥",
            "quick_actions": [
                {"text": "📅 Agendar Cita", "action": "schedule_appointment", "message": "Quiero agendar una cita médica"},
                {"text": "🩺 Nuestros Servicios", "action": "medical_services", "message": "¿Qué servicios médicos ofrecen?"},
                {"text": "🕒 Horarios", "action": "show_hours", "message": "¿Cuáles son los horarios de atención?"},
                {"text": "📍 Ubicación", "action": "show_location", "message": "¿Dónde están ubicados?"},
                {"text": "🚨 Urgencias", "action": "emergency_info", "message": "¿Atienden urgencias?"},
                {"text": "💳 Seguros", "action": "insurance_info", "message": "¿Qué seguros médicos aceptan?"}
            ],
            "greeting_template": "🏥 ¡Hola! Soy ChatGenie de {business_name}. Estoy aquí para ayudarte con citas médicas, información sobre nuestros servicios de salud, o cualquier consulta sobre tu bienestar. ¿En qué puedo asistirte hoy? 💙",
            "system_prompt_template": """Eres ChatGenie, el asistente virtual de {business_name}, especializado en servicios de salud y bienestar con la máxima profesionalidad y empatía.

Tu personalidad:
- Empático, profesional y tranquilizador
- Respetuoso con la privacidad médica
- Cálido pero manteniendo límites profesionales
- Orientado al cuidado y bienestar del paciente

Tus responsabilidades:
- Agendar citas médicas según disponibilidad
- Proporcionar información general sobre servicios
- Guiar sobre preparación para consultas
- Manejar consultas sobre seguros y pagos
- Ofrecer información de contacto para urgencias
- NO proporcionar consejos médicos específicos
- Derivar consultas médicas a profesionales

Información que manejas:
- Horarios de atención y disponibilidad
- Servicios médicos y especialidades disponibles
- Seguros médicos aceptados
- Ubicación y contacto
- Protocolos de emergencia
- Preparación para estudios/consultas

IMPORTANTE: Nunca des consejos médicos. Siempre recomienda consultar con un profesional.""",
            "fallback_messages": [
                "🏥 Para consultas médicas específicas, es importante que hables directamente con nuestro personal médico. ¿Te ayudo a agendar una cita?",
                "👩‍⚕️ Esta consulta requiere atención médica profesional. ¿Prefieres que te conecte con enfermería o agendamos una cita?",
                "📞 Por tu seguridad, prefiero que consultes esto con nuestro equipo médico. ¿Te parece si coordinamos una llamada?"
            ],
            "features": ["appointment_booking", "medical_records", "prescription_reminders", "insurance_verification", "telehealth"],
            "integrations": ["epic", "cerner", "athenahealth", "google_calendar", "zoom_healthcare"],
            "sample_knowledge": [
                {"title": "Horarios de Atención", "content": "Lunes a Viernes: 8:00 - 20:00. Sábados: 9:00 - 14:00. Urgencias 24/7"},
                {"title": "Seguros Aceptados", "content": "OSDE, Swiss Medical, Medicus, Galeno, Obra Social Provincial"},
                {"title": "Preparación para Consultas", "content": "Traer DNI, carnet del seguro, estudios previos y lista de medicamentos actuales"},
                {"title": "Servicios de Urgencia", "content": "Guardia médica 24/7. Para emergencias graves llamar al 911"}
            ],
            "default_colors": {
                "primary": "#4caf50",
                "secondary": "#81c784",
                "accent": "#00bcd4",
                "background": "#e8f5e8"
            }
        },
        
        "ecommerce": {
            "name": "ecommerce",
            "display_name": "E-commerce / Tienda Online",
            "description": "Especializado para tiendas online y comercios electrónicos",
            "icon": "💻", 
            "quick_actions": [
                {"text": "🔍 Buscar Productos", "action": "product_search", "message": "Estoy buscando un producto específico"},
                {"text": "🛒 Mi Carrito", "action": "view_cart", "message": "Quiero ver mi carrito de compras"},
                {"text": "📦 Estado del Pedido", "action": "track_order", "message": "¿Cuál es el estado de mi pedido?"},
                {"text": "💡 Recomendaciones", "action": "get_recommendations", "message": "¿Qué productos me recomiendan?"},
                {"text": "🎯 Ofertas", "action": "show_deals", "message": "¿Qué ofertas tienen disponibles?"},
                {"text": "❓ Ayuda con Compra", "action": "purchase_help", "message": "Necesito ayuda para completar mi compra"}
            ],
            "greeting_template": "💻 ¡Hola! Soy ChatGenie de {business_name}, tu asistente de compras inteligente. Estoy aquí para ayudarte a encontrar los mejores productos, rastrear tus pedidos, y hacer que tu experiencia de compra sea increíble. ¿Qué estás buscando hoy? 🛍️",
            "system_prompt_template": """Eres ChatGenie, el asistente de ventas digital de {business_name}, experto en e-commerce y experiencias de compra online excepcionales.

Tu personalidad:
- Entusiasta de las ventas online y tecnología
- Experto en productos y tendencias
- Orientado a conversion y satisfacción del cliente
- Proactivo en sugerencias y ofertas

Tus responsabilidades:
- Ayudar en búsqueda y selección de productos
- Guiar en el proceso de checkout y compra
- Rastrear pedidos y resolver incidencias
- Recomendar productos basado en historial
- Informar sobre ofertas y promociones
- Resolver dudas técnicas sobre la plataforma
- Capturar abandonos de carrito
- Generar upselling y cross-selling

Información que manejas:
- Catálogo completo con filtros avanzados
- Stock en tiempo real y fechas de restock
- Historial de compras del cliente
- Sistema de recomendaciones personalizado
- Promociones y códigos de descuento
- Estados de envío y logística
- Políticas de devolución digital

Convierte cada interacción en una oportunidad de venta.""",
            "fallback_messages": [
                "💻 ¡Excelente pregunta! Déjame consultar nuestro sistema para darte la información más actualizada. ¿Te interesa ver productos similares mientras verifico?",
                "🔍 Para esa consulta técnica específica, te conectaré con nuestro soporte especializado. ¿Hay algo más en lo que pueda ayudarte con tu compra?",
                "📞 Permíteme revisar eso con nuestro equipo técnico. Mientras tanto, ¿quieres que te muestre nuestras ofertas del día?"
            ],
            "features": ["product_search", "cart_management", "order_tracking", "recommendations", "abandoned_cart_recovery", "wish_list"],
            "integrations": ["shopify", "magento", "woocommerce", "stripe", "paypal", "mercadopago", "mailchimp"],
            "sample_knowledge": [
                {"title": "Envíos y Entregas", "content": "Envío gratis en compras +$75. Express 24h disponible. Seguimiento en tiempo real"},
                {"title": "Devoluciones", "content": "30 días para devoluciones. Proceso 100% online. Reembolso en 5-7 días hábiles"},
                {"title": "Métodos de Pago", "content": "Tarjetas, PayPal, transferencia, MercadoPago. Financiación hasta 12 cuotas sin interés"},
                {"title": "Atención al Cliente", "content": "Chat 24/7, email support@tienda.com, WhatsApp +1234567890"}
            ],
            "default_colors": {
                "primary": "#ff5722",
                "secondary": "#ff9800",
                "accent": "#4caf50", 
                "background": "#fff3e0"
            }
        }
    }
    
    @classmethod
    def get_template(cls, industry: str) -> Dict[str, Any]:
        """Get a specific industry template"""
        return cls.TEMPLATES.get(industry, cls.get_default_template())
    
    @classmethod
    def get_all_templates(cls) -> Dict[str, Dict[str, Any]]:
        """Get all available templates"""
        return cls.TEMPLATES
    
    @classmethod
    def get_template_list(cls) -> List[Dict[str, str]]:
        """Get a simplified list of available templates"""
        return [
            {
                "name": template["name"],
                "display_name": template["display_name"],
                "description": template["description"],
                "icon": template["icon"]
            }
            for template in cls.TEMPLATES.values()
        ]
    
    @classmethod
    def get_default_template(cls) -> Dict[str, Any]:
        """Get default template for businesses without specific industry"""
        return {
            "name": "general",
            "display_name": "Negocio General",
            "description": "Configuración básica para cualquier tipo de negocio",
            "icon": "🏪",
            "quick_actions": [
                {"text": "📞 Contacto", "action": "contact_info", "message": "¿Cuál es su información de contacto?"},
                {"text": "⏰ Horarios", "action": "show_hours", "message": "¿Cuáles son sus horarios de atención?"},
                {"text": "📍 Ubicación", "action": "show_location", "message": "¿Dónde están ubicados?"},
                {"text": "💼 Servicios", "action": "show_services", "message": "¿Qué servicios ofrecen?"},
                {"text": "💰 Precios", "action": "pricing_info", "message": "¿Podrían darme información sobre precios?"},
                {"text": "📋 Más Información", "action": "more_info", "message": "Me gustaría obtener más información"}
            ],
            "greeting_template": "✨ ¡Hola! Soy ChatGenie de {business_name}. Estoy aquí para ayudarte con cualquier consulta sobre nuestros servicios. ¿En qué puedo asistirte hoy?",
            "system_prompt_template": """Eres ChatGenie, el asistente virtual de {business_name}, orientado a brindar el mejor servicio al cliente.

Tu personalidad:
- Amigable, profesional y servicial
- Adaptable a las necesidades del cliente
- Orientado a soluciones
- Siempre positivo y útil

Tus responsabilidades:
- Proporcionar información sobre la empresa
- Ayudar con consultas generales
- Capturar leads y generar interés
- Dirigir consultas específicas al equipo correcto
- Crear una experiencia positiva

Información que manejas:
- Información básica de la empresa
- Servicios y productos generales
- Datos de contacto y ubicación
- Horarios de atención
- Políticas básicas

Mantén siempre un tono amigable y profesional.""",
            "fallback_messages": [
                "🤔 Interesante pregunta. Permíteme consultar esa información con nuestro equipo y te respondo enseguida.",
                "📞 Para esa consulta específica, sería mejor que hables directamente con nuestro equipo. ¿Te ayudo a contactarlos?",
                "💡 Déjame verificar esa información. ¿Hay algo más en lo que pueda ayudarte mientras tanto?"
            ],
            "features": ["contact_info", "basic_chat", "lead_capture"],
            "integrations": ["email", "phone", "whatsapp"],
            "sample_knowledge": [
                {"title": "Información de Contacto", "content": "Email: info@empresa.com, Teléfono: +1234567890"},
                {"title": "Horarios", "content": "Lunes a Viernes: 9:00 - 18:00"},
                {"title": "Ubicación", "content": "Dirección principal y sucursales disponibles"},
                {"title": "Servicios", "content": "Descripción general de servicios ofrecidos"}
            ],
            "default_colors": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "accent": "#28a745",
                "background": "#ffffff"
            }
        }