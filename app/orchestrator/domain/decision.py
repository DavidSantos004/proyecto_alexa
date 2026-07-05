from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class DecisionVerdict(StrEnum):
    approved = "approved"
    rejected = "rejected"
    needs_confirmation = "needs_confirmation"


class OrchestratorDecision(BaseModel):
    action_id: str
    verdict: DecisionVerdict
    reason: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
