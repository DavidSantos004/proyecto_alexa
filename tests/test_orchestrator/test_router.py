import httpx
import pytest

from app.main import app


class TestOrchestratorRouter:
    @pytest.fixture
    def client(self):
        transport = httpx.ASGITransport(app=app)
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    async def test_propose_returns_approved_decision(self, client):
        response = await client.post(
            "/orchestrator/propose",
            json={
                "source": "llm",
                "action_type": "device_control",
                "description": "Turn on living room light",
                "parameters": {"device_id": "light.living_room", "state": "on"},
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["verdict"] == "approved"
        assert "action_id" in body
        assert "decided_at" in body

    async def test_propose_generates_action_id_when_omitted(self, client):
        response = await client.post(
            "/orchestrator/propose",
            json={
                "source": "voice_command",
                "action_type": "query_info",
                "description": "What is the temperature?",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["action_id"]) == 32
