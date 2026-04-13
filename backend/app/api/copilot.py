from fastapi import APIRouter, HTTPException

from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.services.copilot_service import analyze_ticket

router = APIRouter(
    prefix="/copilot",
    tags=["copilot"],
)


@router.post("/analyze", response_model=CopilotResponse)
def copilot_analyze(data: CopilotRequest) -> CopilotResponse:
    """
    Analyze a support ticket and return a structured AI-Copilot response.

    - **body** (required): the full text of the support ticket.
    - **title** (optional): a short summary or subject of the ticket.

    The response includes:
    - `category`: FAQ | PROCESS | ESCALATE
    - `confidence_score`: 0.0 – 1.0
    - `decision`: auto_reply | escalate
    - `suggested_reply`: ready-to-send reply (null when escalating)
    - `escalation_reason`: why escalation was triggered (null when not escalating)
    - `reasoning_summary`: plain-text explanation of the decision
    - `sources`: list of KB entries used to build the reply
    """
    try:
        return analyze_ticket(title=data.title, body=data.body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
