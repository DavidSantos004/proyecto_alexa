from app.devices.client import HomeAssistantClient
from app.devices.domain.models import DeviceCommand


class TestHomeAssistantClient:
    def test_returns_error_when_token_not_configured(self):
        client = HomeAssistantClient(token="")
        command = DeviceCommand(
            device_id="light.test",
            domain="light",
            service="turn_on",
        )

        result = client.execute(command)

        assert result.success is False
        assert "HA_TOKEN" in result.message
