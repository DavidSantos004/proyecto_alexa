from app.devices.domain.models import DeviceCommand, DeviceResult
from app.devices.ports.device_port import DevicePort
from app.orchestrator.domain.proposed_action import ProposedAction


class DeviceService:
    def __init__(self, device: DevicePort):
        self._device = device

    def execute(self, action: ProposedAction) -> DeviceResult:
        params = action.parameters
        command = DeviceCommand(
            device_id=params.get("device_id", "unknown"),
            domain=params.get("domain", self._infer_domain(action)),
            service=params.get("service", self._infer_service(action)),
            data=params.get("data", {}),
        )
        return self._device.execute(command)

    def _infer_domain(self, action: ProposedAction) -> str:
        device_id = action.parameters.get("device_id", "")
        return device_id.split(".")[0] if "." in device_id else "switch"

    def _infer_service(self, action: ProposedAction) -> str:
        state = action.parameters.get("state", "")
        if state in ("on", "off"):
            return f"turn_{state}"
        if state == "unlock":
            return "open"
        return "turn_on"
