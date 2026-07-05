from collections.abc import Sequence

from app.memory.domain.models import ConversationEntry, Fact
from app.memory.domain.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository):
        self._repository = repository

    def remember(self, key: str, value: str, source: str = "system") -> Fact:
        fact = Fact(key=key, value=value, source=source)
        return self._repository.save_fact(fact)

    def recall(self, key: str) -> str | None:
        fact = self._repository.get_fact(key)
        return fact.value if fact else None

    def search(self, prefix: str) -> Sequence[Fact]:
        return self._repository.list_facts(prefix=prefix)

    def forget(self, key: str) -> bool:
        return self._repository.delete_fact(key)

    def log_conversation(
        self,
        user_input: str,
        system_response: str | None = None,
        action_summary: dict | None = None,
        decision_verdict: str | None = None,
        decision_reason: str | None = None,
    ) -> ConversationEntry:
        entry = ConversationEntry(
            user_input=user_input,
            system_response=system_response,
            action_summary=action_summary,
            decision_verdict=decision_verdict,
            decision_reason=decision_reason,
        )
        return self._repository.save_conversation(entry)

    def get_history(self, limit: int = 10) -> Sequence[ConversationEntry]:
        return self._repository.get_recent_conversations(limit=limit)
