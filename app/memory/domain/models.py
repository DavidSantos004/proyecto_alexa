from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class Fact(BaseModel):
    fact_id: str = Field(default_factory=lambda: uuid4().hex)
    key: str
    value: str
    source: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: uuid4().hex)
    user_input: str
    system_response: str | None = None
    action_summary: dict | None = None
    decision_verdict: str | None = None
    decision_reason: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
