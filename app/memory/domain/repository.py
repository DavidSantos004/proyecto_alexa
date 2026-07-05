from collections.abc import Sequence
from typing import Protocol

from app.memory.domain.models import ConversationEntry, Fact


class MemoryRepository(Protocol):
    def save_fact(self, fact: Fact) -> Fact:
        ...

    def get_fact(self, key: str) -> Fact | None:
        ...

    def list_facts(self, prefix: str | None = None) -> Sequence[Fact]:
        ...

    def delete_fact(self, key: str) -> bool:
        ...

    def save_conversation(self, entry: ConversationEntry) -> ConversationEntry:
        ...

    def get_recent_conversations(self, limit: int = 10) -> Sequence[ConversationEntry]:
        ...
