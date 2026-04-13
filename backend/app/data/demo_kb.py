"""
Demo knowledge base for the Atiende24 Copilot MVP.

Each entry represents a support knowledge-base article that the copilot
uses to retrieve context when analysing incoming tickets.
"""

from typing import List, TypedDict


class KBEntry(TypedDict):
    id: str
    title: str
    content: str


DEMO_KB: List[KBEntry] = [
    {
        "id": "kb-001",
        "title": "Política de devoluciones",
        "content": (
            "Aceptamos devoluciones dentro de los 30 días siguientes a la compra. "
            "El producto debe estar en perfecto estado y en su embalaje original. "
            "El reembolso se realiza en 5-7 días hábiles una vez recibido el artículo."
        ),
    },
    {
        "id": "kb-002",
        "title": "Horario de atención al cliente",
        "content": (
            "Nuestro equipo de soporte está disponible de lunes a viernes de 9:00 a 18:00 "
            "(hora peninsular). Los fines de semana y festivos solo atendemos urgencias "
            "a través del correo urgencias@empresa.com."
        ),
    },
    {
        "id": "kb-003",
        "title": "Tiempo de envío y entrega",
        "content": (
            "Los pedidos nacionales peninsulares se entregan en 24-48 horas hábiles. "
            "Para Islas Canarias, Baleares y Ceuta/Melilla el plazo es de 3-5 días hábiles. "
            "Los envíos internacionales tardan entre 7 y 15 días hábiles."
        ),
    },
    {
        "id": "kb-004",
        "title": "Cómo rastrear un pedido",
        "content": (
            "Una vez enviado el pedido, recibirás un correo electrónico con el número de "
            "seguimiento. Puedes rastrearlo en nuestra web en la sección 'Mis pedidos' o "
            "directamente en la web del transportista indicado en el email."
        ),
    },
    {
        "id": "kb-005",
        "title": "Proceso de cambio de producto",
        "content": (
            "Para cambiar un producto, accede a 'Mis pedidos', selecciona el artículo y "
            "elige 'Solicitar cambio'. Tienes un plazo de 15 días desde la recepción. "
            "Los cambios se gestionan en 3-5 días hábiles tras la recepción del artículo devuelto."
        ),
    },
    {
        "id": "kb-006",
        "title": "Métodos de pago aceptados",
        "content": (
            "Aceptamos tarjeta de crédito/débito (Visa, Mastercard, Amex), PayPal, "
            "transferencia bancaria y pago contra reembolso. Todos los pagos se procesan "
            "mediante pasarela segura con cifrado SSL."
        ),
    },
    {
        "id": "kb-007",
        "title": "Cómo cancelar un pedido",
        "content": (
            "Puedes cancelar un pedido antes de que sea enviado accediendo a 'Mis pedidos' "
            "y seleccionando 'Cancelar pedido'. Si el pedido ya está en tránsito, deberás "
            "esperar a recibirlo y gestionar la devolución en los plazos indicados."
        ),
    },
    {
        "id": "kb-008",
        "title": "Soporte técnico para productos electrónicos",
        "content": (
            "Para problemas técnicos con productos electrónicos, contacta a nuestro equipo "
            "técnico a través de soporte.tecnico@empresa.com o llama al 900-XXX-XXX en "
            "horario de atención. Para averías en garantía, adjunta foto del producto y "
            "número de pedido."
        ),
    },
    {
        "id": "kb-009",
        "title": "Garantía de productos",
        "content": (
            "Todos nuestros productos incluyen garantía mínima de 2 años conforme a la "
            "normativa europea. Para ejercer la garantía, conserva el ticket de compra o "
            "número de pedido y contacta con soporte indicando el defecto detectado."
        ),
    },
    {
        "id": "kb-010",
        "title": "Facturación y facturas",
        "content": (
            "Las facturas se generan automáticamente tras cada compra y se envían por email. "
            "Si necesitas una factura con datos de empresa, indícalo al realizar el pedido "
            "introduciendo el CIF/NIF en los datos de facturación. Puedes descargar facturas "
            "anteriores desde tu área de cliente."
        ),
    },
    # ------------------------------------------------------------------
    # Soporte interno (IT helpdesk + RRHH) — demo Sprint 1
    # ------------------------------------------------------------------
    {
        "id": "kb-101",
        "title": "Restablecer contraseña corporativa: acceso bloqueado y recuperación",
        "content": (
            "Si olvidaste tu contraseña o tu cuenta está bloqueada, accede al portal en "
            "intranet.empresa.com/reset-password e introduce tu correo corporativo para "
            "restablecer la contraseña. Recibirás un enlace válido durante 30 minutos. "
            "La nueva contraseña debe tener mínimo 10 caracteres con mayúscula, número y símbolo. "
            "Si intentaste entrar varias veces y la cuenta queda bloqueada, espera 15 minutos "
            "o abre un ticket indicando tu nombre y departamento para desbloqueo manual."
        ),
    },
    {
        "id": "kb-102",
        "title": "Acceso VPN corporativa (GlobalProtect)",
        "content": (
            "Descarga GlobalProtect desde intranet.empresa.com/vpn e introduce el servidor "
            "vpn.empresa.com. Inicia sesión con tus credenciales corporativas y acepta el "
            "segundo factor de autenticación (2FA) en tu móvil. Problemas frecuentes: "
            "error de certificado → ejecuta Renovar certificado desde el icono de GlobalProtect; "
            "2FA no llega → verifica que tu teléfono en el directorio sea correcto."
        ),
    },
    {
        "id": "kb-103",
        "title": "Solicitud de equipo informático y accesorios",
        "content": (
            "Accede al portal intranet.empresa.com/hardware y selecciona Nueva solicitud → "
            "Equipo informático. Indica el motivo (equipo nuevo, sustitución, daño o robo). "
            "Tu manager debe aprobar en 3 días hábiles; el equipo se entrega en 5-10 días. "
            "Los accesorios (ratón, teclado, monitor, hub USB) se solicitan en la misma pantalla "
            "marcando la casilla Incluir accesorios."
        ),
    },
    {
        "id": "kb-104",
        "title": "Solicitud de vacaciones y permisos",
        "content": (
            "Entra en intranet.empresa.com/rrhh, ve a Mis solicitudes → Vacaciones, "
            "selecciona el rango de fechas y envía para aprobación. El manager tiene 5 días hábiles "
            "para aprobar o rechazar. El saldo de días disponibles se consulta en "
            "Mi perfil → Saldo vacacional. Para bajas médicas de más de 3 días entrega el "
            "parte médico a RRHH en un plazo máximo de 72 horas."
        ),
    },
    {
        "id": "kb-105",
        "title": "Reembolso de gastos: cómo solicitar el reembolso de un gasto de empresa",
        "content": (
            "Para solicitar el reembolso de un gasto corporativo, guarda los justificantes "
            "(facturas con IVA desglosado) y accede a intranet.empresa.com/gastos para crear "
            "un nuevo informe de gastos. Sube las imágenes de los justificantes (JPG, PNG o PDF, "
            "máx. 5 MB). Indica el centro de coste y envía para aprobación del manager. "
            "Si el informe se envía antes del día 20, el reembolso se incluye en la siguiente nómina. "
            "Límites por gasto: comidas 50 € por persona, taxi 30 € por trayecto, "
            "hotel 120 € por noche, formación 200 € por curso."
        ),
    },
    {
        "id": "kb-106",
        "title": "Licencias de software corporativo",
        "content": (
            "Consulta el catálogo en intranet.empresa.com/software-catalog. El software disponible "
            "sin solicitud adicional incluye: Microsoft 365 (Word, Excel, PowerPoint, Teams, Outlook), "
            "Adobe Acrobat Reader, Zoom, Slack, GitHub corporativo y Visual Studio Code. "
            "Para instalar, pulsa el botón Instalar; el despliegue tarda menos de 30 minutos. "
            "Si necesitas software que no está en el catálogo, abre un ticket con el nombre, "
            "versión y justificación de negocio."
        ),
    },
    {
        "id": "kb-107",
        "title": "Impresoras corporativas: conexión y problemas frecuentes",
        "content": (
            "En Windows: Configuración → Bluetooth y dispositivos → Impresoras y escáneres → "
            "Agregar dispositivo. En macOS: Preferencias del sistema → Impresoras y escáneres → +. "
            "IPs por planta: Planta 1 HP LaserJet 10.0.1.10, Planta 2 Canon imageRUNNER 10.0.2.10, "
            "Planta 3 Ricoh IM C300 10.0.3.10. Problema frecuente: impresora sin respuesta → "
            "apágala 30 segundos y vuelve a encenderla; si continúa, abre ticket de soporte."
        ),
    },
    {
        "id": "kb-108",
        "title": "Reserva de salas de reuniones",
        "content": (
            "Reserva salas de reuniones a través de Microsoft Outlook o Teams creando un evento "
            "y agregando la sala en el campo correspondiente. Salas disponibles: Sala Norte 1 "
            "(6 personas, TV 55\"), Sala Norte 2 (10 personas, proyector), Sala Sur (4 personas), "
            "Sala Dirección (20 personas, proyector 4K). Las reservas no usadas se liberan "
            "automáticamente a los 15 minutos. Máximo 4 horas por reserva."
        ),
    },
    {
        "id": "kb-109",
        "title": "Política de seguridad TI: contraseñas, dispositivos y phishing",
        "content": (
            "Contraseñas: mínimo 10 caracteres, cambio obligatorio cada 90 días, no reutilices "
            "las últimas 5 contraseñas. Dispositivos: bloquea la pantalla al ausentarte "
            "(Win+L / Cmd+Ctrl+Q), no conectes USB desconocidos, no instales software no autorizado. "
            "Phishing: reporta correos sospechosos reenviándolos a seguridad@empresa.com; "
            "nunca facilites credenciales por correo aunque parezca un mensaje interno."
        ),
    },
    {
        "id": "kb-110",
        "title": "Proceso de onboarding para nuevas incorporaciones",
        "content": (
            "Antes del primer día RRHH envía un correo con el enlace de activación de cuenta y la "
            "guía de bienvenida. El primer día incluye: entrega de tarjeta de acceso, firma de "
            "contrato, entrega del equipo informático, tour por las instalaciones y presentación "
            "con el equipo. El manager debe abrir un ticket de soporte 3 días antes solicitando: "
            "cuenta de email, acceso VPN, repositorios, licencias de software y tarjeta de acceso físico."
        ),
    },
]
