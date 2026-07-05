from app.devices.domain.models import DeviceCommand, DeviceResult
from app.devices.service import DeviceService
from app.orchestrator.domain.proposed_action import (
    ActionSource,
    ActionType,
    ProposedAction,
    RiskLevel,
)


class FakeDevice:
    def __init__(self):
        self.last_command: DeviceCommand | None = None

    def execute(self, command: DeviceCommand) -> DeviceResult:
        self.last_command = command
        return DeviceResult(success=True, message="ok", state={"state": "on"})


class TestDeviceService:
    def setup_method(self):
        self.device = FakeDevice()
        self.service = DeviceService(self.device)

    def test_execute_light_on(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Turn on living room light",
            parameters={"device_id": "light.living_room", "state": "on"},
        )

        result = self.service.execute(action)

        assert result.success is True
        assert self.device.last_command is not None
        assert self.device.last_command.device_id == "light.living_room"
        assert self.device.last_command.domain == "light"
        assert self.device.last_command.service == "turn_on"

    def test_execute_infers_domain_from_device_id(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Lock front door",
            parameters={"device_id": "lock.front_door", "state": "lock"},
        )

        self.service.execute(action)

        assert self.device.last_command.domain == "lock"
        assert self.device.last_command.service == "turn_on"

    def test_execute_unlock_uses_open_service(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Unlock front door",
            parameters={"device_id": "lock.front_door", "state": "unlock"},
            risk_level=RiskLevel.high,
            requires_confirmation=True,
        )

        self.service.execute(action)

        assert self.device.last_command.service == "open"

    def test_execute_passes_extra_parameters_as_data(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Set light brightness",
            parameters={
                "device_id": "light.living_room",
                "state": "on",
                "data": {"brightness": 128, "color": "warm"},
            },
        )

        self.service.execute(action)

        assert self.device.last_command.data == {"brightness": 128, "color": "warm"}
