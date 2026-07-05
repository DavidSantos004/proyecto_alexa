import json
from collections.abc import Sequence

from sqlalchemy import select

from app.infrastructure.database import get_session
from app.memory.domain.models import ConversationEntry, Fact
from app.memory.orm import ConversationModel, FactModel


class SqlAlchemyMemoryRepository:
    def save_fact(self, fact: Fact) -> Fact:
        with get_session() as session:
            existing = session.execute(
                select(FactModel).where(FactModel.key == fact.key)
            ).scalar_one_or_none()

            if existing:
                existing.value = fact.value
                existing.source = fact.source
                existing.updated_at = fact.updated_at
                row = existing
            else:
                row = FactModel(**fact.model_dump())
                session.add(row)

            session.commit()
            return fact

    def get_fact(self, key: str) -> Fact | None:
        with get_session() as session:
            row = session.execute(
                select(FactModel).where(FactModel.key == key)
            ).scalar_one_or_none()

            if row is None:
                return None

            return Fact(
                fact_id=row.fact_id,
                key=row.key,
                value=row.value,
                source=row.source,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def list_facts(self, prefix: str | None = None) -> Sequence[Fact]:
        with get_session() as session:
            stmt = select(FactModel)
            if prefix:
                stmt = stmt.where(FactModel.key.startswith(prefix))
            stmt = stmt.order_by(FactModel.key)
            rows = session.execute(stmt).scalars().all()

            return [
                Fact(
                    fact_id=row.fact_id,
                    key=row.key,
                    value=row.value,
                    source=row.source,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row in rows
            ]

    def delete_fact(self, key: str) -> bool:
        with get_session() as session:
            row = session.execute(
                select(FactModel).where(FactModel.key == key)
            ).scalar_one_or_none()

            if row is None:
                return False

            session.delete(row)
            session.commit()
            return True

    def save_conversation(self, entry: ConversationEntry) -> ConversationEntry:
        with get_session() as session:
            row = ConversationModel(
                entry_id=entry.entry_id,
                user_input=entry.user_input,
                system_response=entry.system_response,
                action_summary=(
                    json.dumps(entry.action_summary) if entry.action_summary else None
                ),
                decision_verdict=entry.decision_verdict,
                decision_reason=entry.decision_reason,
                timestamp=entry.timestamp,
            )
            session.add(row)
            session.commit()
            return entry

    def get_recent_conversations(self, limit: int = 10) -> Sequence[ConversationEntry]:
        with get_session() as session:
            stmt = (
                select(ConversationModel)
                .order_by(ConversationModel.timestamp.desc())
                .limit(limit)
            )
            rows = session.execute(stmt).scalars().all()

            return [
                ConversationEntry(
                    entry_id=row.entry_id,
                    user_input=row.user_input,
                    system_response=row.system_response,
                    action_summary=(
                        json.loads(row.action_summary) if row.action_summary else None
                    ),
                    decision_verdict=row.decision_verdict,
                    decision_reason=row.decision_reason,
                    timestamp=row.timestamp,
                )
                for row in reversed(rows)
            ]
