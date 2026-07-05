from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class ActionSource(StrEnum):
    llm = "llm"
    voice_command = "voice_command"
    automation_trigger = "automation_trigger"
    manual_api = "manual_api"


class ActionType(StrEnum):
    device_control = "device_control"
    notification = "notification"
    query_info = "query_info"
    automation_change = "automation_change"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class ProposedAction(BaseModel):
    action_id: str = Field(default_factory=lambda: uuid4().hex)
    source: ActionSource
    action_type: ActionType
    description: str
    parameters: dict = Field(default_factory=dict)
    risk_level: RiskLevel = Field(default=RiskLevel.low)
    requires_confirmation: bool = Field(default=False)
    proposed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
