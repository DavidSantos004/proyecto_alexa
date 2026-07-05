from app.api.service import ChatService
from app.devices.domain.models import DeviceResult
from app.llm_service.domain.models import LLMResponse
from app.orchestrator.domain.decision import DecisionVerdict, OrchestratorDecision
from app.orchestrator.domain.proposed_action import (
    ActionSource,
    ActionType,
    ProposedAction,
)


class FakeLLM:
    def __init__(self):
        self.last_context = None

    def propose(self, context):
        self.last_context = context
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Turn on living room light",
            parameters={"device_id": "light.living_room", "state": "on"},
        )
        return LLMResponse(raw_text="{}", parsed_action=action)


class FakeFailingLLM:
    def propose(self, context):
        return LLMResponse(raw_text="bad", error="Could not parse JSON")


class FakeOrchestrator:
    def __init__(self):
        self.last_action = None

    def decide(self, action):
        self.last_action = action
        return OrchestratorDecision(
            action_id=action.action_id,
            verdict=DecisionVerdict.approved,
            reason="ok",
        )


class FakeMemory:
    def __init__(self):
        self.conversations = []

    def log_conversation(self, **kwargs):
        self.conversations.append(kwargs)

    def get_history(self, limit=10):
        return list(reversed(self.conversations[-limit:]))


class FakeDevice:
    def __init__(self):
        self.last_action = None

    def execute(self, action):
        self.last_action = action
        return DeviceResult(success=True, message="ok", state={"state": "on"})


class TestChatService:
    def setup_method(self):
        self.llm = FakeLLM()
        self.orchestrator = FakeOrchestrator()
        self.memory = FakeMemory()
        self.device = FakeDevice()
        self.service = ChatService(
            llm=self.llm,
            orchestrator=self.orchestrator,
            memory=self.memory,
            devices=self.device,
        )

    def test_process_message_returns_decision(self):
        result = self.service.process_message("turn on the light")

        assert result["status"] == "ok"
        assert result["action"]["action_type"] == "device_control"
        assert result["decision"]["verdict"] == "approved"

    def test_process_message_executes_device_action(self):
        result = self.service.process_message("turn on the light")

        assert result["device_result"] is not None
        assert result["device_result"]["success"] is True
        assert self.device.last_action is not None

    def test_process_message_logs_to_memory(self):
        self.service.process_message("turn on the light")

        assert len(self.memory.conversations) == 1
        assert self.memory.conversations[0]["user_input"] == "turn on the light"

    def test_process_message_with_failing_llm(self):
        self.service = ChatService(
            llm=FakeFailingLLM(),
            orchestrator=self.orchestrator,
            memory=self.memory,
            devices=self.device,
        )

        result = self.service.process_message("do something")

        assert result["status"] == "error"
        assert "Could not parse" in result["message"]

    def test_process_message_does_not_execute_on_llm_failure(self):
        self.service = ChatService(
            llm=FakeFailingLLM(),
            orchestrator=self.orchestrator,
            memory=self.memory,
            devices=self.device,
        )

        self.service.process_message("do something")

        assert self.device.last_action is None
