from pydantic import BaseModel


class DeviceCommand(BaseModel):
    device_id: str
    domain: str
    service: str
    data: dict = {}


class DeviceResult(BaseModel):
    success: bool
    message: str
    state: dict | None = None
