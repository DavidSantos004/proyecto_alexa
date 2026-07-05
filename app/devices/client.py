import os

import httpx

from app.devices.domain.models import DeviceCommand, DeviceResult

HA_BASE_URL = os.getenv("HA_BASE_URL", "http://homeassistant:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")


class HomeAssistantClient:
    def __init__(self, base_url: str = HA_BASE_URL, token: str = HA_TOKEN):
        self._base_url = base_url
        self._token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def execute(self, command: DeviceCommand) -> DeviceResult:
        if not self._token:
            return DeviceResult(
                success=False,
                message="HA_TOKEN not configured. Set HA_TOKEN env var.",
            )

        try:
            payload = {"entity_id": command.device_id} | command.data
            response = httpx.post(
                f"{self._base_url}/api/services/{command.domain}/{command.service}",
                headers=self._headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            msg = f"{command.domain}.{command.service} on {command.device_id}"
            return DeviceResult(
                success=True,
                message=msg,
                state=response.json(),
            )
        except httpx.HTTPStatusError as e:
            msg = f"HA error: {e.response.status_code} - {e.response.text}"
            return DeviceResult(
                success=False,
                message=msg,
            )
        except httpx.RequestError as e:
            return DeviceResult(
                success=False,
                message=f"Cannot reach Home Assistant at {self._base_url}: {e}",
            )
