from app.llm_service.domain.models import LLMContext
from app.llm_service.service import LLMService


class FakeLLM:
    def __init__(self, response: str = ""):
        self._response = response
        self.last_prompt: str | None = None

    def generate(self, prompt: str, model: str = "qwen2.5:3b") -> str:
        self.last_prompt = prompt
        return self._response


VALID_ACTION_JSON = """{
  "source": "llm",
  "action_type": "device_control",
  "description": "Turn on living room light",
  "parameters": {"device": "light.living_room", "state": "on"},
  "risk_level": "low",
  "requires_confirmation": false
}"""


class TestLLMService:
    def setup_method(self):
        self.context = LLMContext(user_input="turn on the light")

    def test_propose_returns_parsed_action(self):
        llm = FakeLLM(response=VALID_ACTION_JSON)
        service = LLMService(llm)

        result = service.propose(self.context)

        assert result.error is None
        assert result.parsed_action is not None
        assert result.parsed_action.action_type.value == "device_control"
        assert result.parsed_action.description == "Turn on living room light"

    def test_propose_includes_user_input_in_prompt(self):
        llm = FakeLLM(response=VALID_ACTION_JSON)
        service = LLMService(llm)

        service.propose(self.context)

        assert llm.last_prompt is not None
        assert "turn on the light" in llm.last_prompt

    def test_propose_handles_invalid_json(self):
        llm = FakeLLM(response="this is not json")
        service = LLMService(llm)

        result = service.propose(self.context)

        assert result.parsed_action is None
        assert result.error is not None

    def test_propose_handles_llm_exception(self):
        class FailingLLM:
            def generate(self, prompt: str, model: str = "") -> str:
                raise ConnectionError("Ollama not available")

        service = LLMService(FailingLLM())
        result = service.propose(self.context)

        assert result.parsed_action is None
        assert "LLM call failed" in result.error

    def test_propose_strips_markdown_code_block(self):
        llm = FakeLLM(response=f"```json\n{VALID_ACTION_JSON}\n```")
        service = LLMService(llm)

        result = service.propose(self.context)

        assert result.parsed_action is not None
        assert result.error is None

    def test_propose_includes_context_facts_in_prompt(self):
        context = LLMContext(
            user_input="set temperature to 22",
            facts=[{"key": "user.preferred_temp", "value": "22"}],
        )
        llm = FakeLLM(response=VALID_ACTION_JSON)
        service = LLMService(llm)

        service.propose(context)

        assert "user.preferred_temp" in llm.last_prompt
        assert "22" in llm.last_prompt

    def test_propose_includes_recent_history_in_prompt(self):
        context = LLMContext(
            user_input="turn off the light",
            recent_history=[
                {"user_input": "turn on the light"},
            ],
        )
        llm = FakeLLM(response=VALID_ACTION_JSON)
        service = LLMService(llm)

        service.propose(context)

        assert "turn on the light" in llm.last_prompt
