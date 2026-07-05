import os
from collections.abc import Sequence

from app.devices.client import HomeAssistantClient
from app.devices.service import DeviceService
from app.llm_service.client import OllamaClient
from app.llm_service.service import LLMService
from app.memory.domain.models import ConversationEntry, Fact
from app.memory.domain.repository import MemoryRepository
from app.memory.repository import SqlAlchemyMemoryRepository
from app.memory.service import MemoryService
from app.orchestrator.service import OrchestratorService

USE_FAKES = os.getenv("JARVIS_USE_FAKES", "true").lower() == "true"


def build_chat_service():
    if USE_FAKES:
        llm = _fake_llm()
        memory = MemoryService(_fake_memory_repo())
        devices = _fake_device()
    else:
        llm = LLMService(OllamaClient())
        memory = MemoryService(SqlAlchemyMemoryRepository())
        devices = DeviceService(HomeAssistantClient())

    from app.api.service import ChatService

    return ChatService(
        llm=llm,
        orchestrator=OrchestratorService(),
        memory=memory,
        devices=devices,
    )


def _fake_llm():
    from app.llm_service.domain.models import LLMResponse
    from app.orchestrator.domain.proposed_action import (
        ActionSource,
        ActionType,
        ProposedAction,
    )

    class FakeLLM:
        def propose(self, context):
            action = ProposedAction(
                source=ActionSource.llm,
                action_type=ActionType.device_control,
                description=f"Ejecutar: {context.user_input}",
                parameters={"device_id": "unknown", "state": "on"},
            )
            return LLMResponse(raw_text="{}", parsed_action=action)

    return FakeLLM()


class _InMemoryRepo:
    def __init__(self):
        self._facts: dict[str, Fact] = {}
        self._conversations: list[ConversationEntry] = []

    def save_fact(self, fact: Fact) -> Fact:
        self._facts[fact.key] = fact
        return fact

    def get_fact(self, key: str) -> Fact | None:
        return self._facts.get(key)

    def list_facts(self, prefix: str | None = None) -> Sequence[Fact]:
        if prefix:
            return [f for f in self._facts.values() if f.key.startswith(prefix)]
        return list(self._facts.values())

    def delete_fact(self, key: str) -> bool:
        return self._facts.pop(key, None) is not None

    def save_conversation(self, entry: ConversationEntry) -> ConversationEntry:
        self._conversations.append(entry)
        return entry

    def get_recent_conversations(self, limit: int = 10) -> Sequence[ConversationEntry]:
        return list(reversed(self._conversations[-limit:]))


def _fake_memory_repo() -> MemoryRepository:
    return _InMemoryRepo()


def _fake_device():
    from app.devices.domain.models import DeviceResult

    class FakeDevice:
        def execute(self, action):
            return DeviceResult(
                success=True,
                message=f"Simulado: {action.description}",
                state={"state": "simulated"},
            )

    return FakeDevice()
