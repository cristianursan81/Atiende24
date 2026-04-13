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
]
