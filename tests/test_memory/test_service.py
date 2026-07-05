from collections.abc import Sequence

from app.memory.domain.models import ConversationEntry, Fact
from app.memory.service import MemoryService


class InMemoryRepository:
    def __init__(self):
        self._facts: dict[str, Fact] = {}
        self._conversations: list[ConversationEntry] = []

    def save_fact(self, fact: Fact) -> Fact:
        existing = self._facts.get(fact.key)
        if existing:
            fact.fact_id = existing.fact_id
            fact.created_at = existing.created_at
        self._facts[fact.key] = fact
        return fact

    def get_fact(self, key: str) -> Fact | None:
        return self._facts.get(key)

    def list_facts(self, prefix: str | None = None) -> Sequence[Fact]:
        if prefix:
            return [f for f in self._facts.values() if f.key.startswith(prefix)]
        return list(self._facts.values())

    def delete_fact(self, key: str) -> bool:
        if key in self._facts:
            del self._facts[key]
            return True
        return False

    def save_conversation(self, entry: ConversationEntry) -> ConversationEntry:
        self._conversations.append(entry)
        return entry

    def get_recent_conversations(self, limit: int = 10) -> Sequence[ConversationEntry]:
        return list(reversed(self._conversations[-limit:]))


class TestMemoryService:
    def setup_method(self):
        self.service = MemoryService(InMemoryRepository())

    def test_remember_and_recall(self):
        self.service.remember("user.name", "David", source="user")
        assert self.service.recall("user.name") == "David"

    def test_recall_unknown_key_returns_none(self):
        assert self.service.recall("nonexistent") is None

    def test_remember_updates_existing_key(self):
        self.service.remember("room.temp", "22")
        self.service.remember("room.temp", "23")
        assert self.service.recall("room.temp") == "23"

    def test_search_by_prefix(self):
        self.service.remember("device.light.state", "on")
        self.service.remember("device.lock.state", "locked")
        self.service.remember("user.preference", "dark_mode")

        results = self.service.search("device.")
        assert len(results) == 2
        assert all(f.key.startswith("device.") for f in results)

    def test_forget_existing_key(self):
        self.service.remember("temp", "22")
        assert self.service.forget("temp") is True
        assert self.service.recall("temp") is None

    def test_forget_nonexistent_key(self):
        assert self.service.forget("nothing") is False

    def test_log_and_get_conversation(self):
        self.service.log_conversation(
            user_input="turn on the light",
            system_response="Turning on living room light",
            action_summary={"device": "light.living_room", "state": "on"},
            decision_verdict="approved",
        )

        history = self.service.get_history()
        assert len(history) == 1
        assert history[0].user_input == "turn on the light"
        assert history[0].system_response == "Turning on living room light"
        assert history[0].decision_verdict == "approved"

    def test_get_history_returns_most_recent_first(self):
        self.service.log_conversation(user_input="first")
        self.service.log_conversation(user_input="second")
        self.service.log_conversation(user_input="third")

        history = self.service.get_history(limit=2)
        assert len(history) == 2
        assert history[0].user_input == "third"
        assert history[1].user_input == "second"
