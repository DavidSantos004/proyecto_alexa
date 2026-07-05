from pydantic import BaseModel

from app.orchestrator.domain.proposed_action import ProposedAction


class LLMContext(BaseModel):
    user_input: str
    recent_history: list[dict] = []
    facts: list[dict] = []
    available_actions: list[str] = [
        "device_control",
        "query_info",
        "notification",
        "automation_change",
    ]


class LLMResponse(BaseModel):
    raw_text: str
    parsed_action: ProposedAction | None = None
    error: str | None = None
