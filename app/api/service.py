from app.devices.service import DeviceService
from app.llm_service.domain.models import LLMContext
from app.llm_service.service import LLMService
from app.memory.service import MemoryService
from app.orchestrator.domain.decision import DecisionVerdict
from app.orchestrator.domain.proposed_action import ActionType
from app.orchestrator.service import OrchestratorService


class ChatService:
    def __init__(
        self,
        llm: LLMService,
        orchestrator: OrchestratorService,
        memory: MemoryService,
        devices: DeviceService,
    ):
        self._llm = llm
        self._orchestrator = orchestrator
        self._memory = memory
        self._devices = devices

    def process_message(self, message: str) -> dict:
        context = LLMContext(user_input=message)
        llm_response = self._llm.propose(context)

        action = llm_response.parsed_action

        if action is None:
            self._memory.log_conversation(
                user_input=message,
                system_response=(
                    llm_response.error or "No se pudo entender la solicitud"
                ),
            )
            return {
                "status": "error",
                "message": llm_response.error or "No se pudo entender la solicitud",
            }

        decision = self._orchestrator.decide(action)

        device_result = None
        if (
            decision.verdict == DecisionVerdict.approved
            and action.action_type == ActionType.device_control
        ):
            device_result = self._devices.execute(action)

        self._memory.log_conversation(
            user_input=message,
            system_response=f"Acción: {action.description} — {decision.verdict}",
            action_summary=action.model_dump(mode="json"),
            decision_verdict=decision.verdict.value,
            decision_reason=decision.reason,
        )

        return {
            "status": "ok",
            "action": action.model_dump(),
            "decision": decision.model_dump(),
            "device_result": device_result.model_dump() if device_result else None,
        }
