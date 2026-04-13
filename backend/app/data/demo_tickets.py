"""
Demo tickets for the Atiende24 Copilot MVP.

These sample tickets can be used for manual or automated testing of the
POST /copilot/analyze endpoint.  Each entry includes the expected behaviour
so it is easy to verify the copilot is working correctly.
"""

from typing import Optional, TypedDict


class DemoTicket(TypedDict):
    title: Optional[str]
    body: str
    expected_category: str  # FAQ | PROCESS | ESCALATE


DEMO_TICKETS: list[DemoTicket] = [
    # --- FAQ tickets ---
    {
        "title": "Horario de atención",
        "body": "Hola, ¿cuál es vuestro horario de atención al cliente?",
        "expected_category": "FAQ",
    },
    {
        "title": None,
        "body": "¿Cuánto tarda en llegar un pedido a Canarias?",
        "expected_category": "FAQ",
    },
    {
        "title": "Métodos de pago",
        "body": "¿Puedo pagar con PayPal o solo admitís tarjeta?",
        "expected_category": "FAQ",
    },
    {
        "title": "Garantía",
        "body": "¿Cuánto tiempo de garantía tienen vuestros productos?",
        "expected_category": "FAQ",
    },
    # --- PROCESS tickets ---
    {
        "title": "Quiero devolver un producto",
        "body": "Compré un artículo hace una semana y quiero devolverlo. ¿Cuál es el proceso para hacer la devolución?",
        "expected_category": "PROCESS",
    },
    {
        "title": "Cambio de producto",
        "body": "Necesito cambiar el producto que recibí por una talla diferente. ¿Cómo lo hago?",
        "expected_category": "PROCESS",
    },
    {
        "title": "Cómo rastrear pedido",
        "body": "Mi pedido salió ayer pero no sé cómo seguir el envío. ¿Cómo puedo rastrear mi pedido?",
        "expected_category": "PROCESS",
    },
    {
        "title": "Cancelar pedido",
        "body": "Acabo de hacer un pedido por error y necesito cancelarlo. ¿Qué pasos debo seguir para cancelar el pedido?",
        "expected_category": "PROCESS",
    },
    # --- ESCALATE tickets ---
    {
        "title": "Cobro incorrecto en mi tarjeta",
        "body": "Me habéis cobrado dos veces el mismo pedido. Esto es un error grave y necesito que lo solucionen urgentemente.",
        "expected_category": "ESCALATE",
    },
    {
        "title": "Producto llegó roto",
        "body": "El producto que recibí llegó completamente roto. Es inaceptable y quiero presentar una reclamación formal.",
        "expected_category": "ESCALATE",
    },
    {
        "title": None,
        "body": "Llevo tres semanas esperando mi pedido y nadie me da respuesta. Voy a tener que hablar con mi abogado.",
        "expected_category": "ESCALATE",
    },
]
