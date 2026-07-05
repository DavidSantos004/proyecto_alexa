from typing import Protocol

from app.devices.domain.models import DeviceCommand, DeviceResult


class DevicePort(Protocol):
    def execute(self, command: DeviceCommand) -> DeviceResult:
        ...
