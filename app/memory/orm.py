from datetime import datetime, timezone

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FactModel(Base):
    __tablename__ = "facts"

    fact_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)


class ConversationModel(Base):
    __tablename__ = "conversations"

    entry_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_input: Mapped[str] = mapped_column(Text)
    system_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_verdict: Mapped[str | None] = mapped_column(String(50), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(default=_utcnow)
