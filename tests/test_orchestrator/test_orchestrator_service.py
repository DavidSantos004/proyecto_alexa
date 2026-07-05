from datetime import datetime, timezone

from app.orchestrator.domain.decision import DecisionVerdict
from app.orchestrator.domain.proposed_action import (
    ActionSource,
    ActionType,
    ProposedAction,
    RiskLevel,
)
from app.orchestrator.service import OrchestratorService


class TestOrchestratorService:
    def setup_method(self):
        self.service = OrchestratorService()

    def test_decide_approves_all_actions_in_sprint1(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Turn on living room light",
            parameters={"device_id": "light.living_room", "state": "on"},
            risk_level=RiskLevel.low,
            requires_confirmation=False,
            proposed_at=datetime.now(timezone.utc),
        )

        decision = self.service.decide(action)

        assert decision.verdict == DecisionVerdict.approved
        assert "Sprint 1" in decision.reason

    def test_decide_accepts_high_risk_actions_too_for_now(self):
        action = ProposedAction(
            source=ActionSource.llm,
            action_type=ActionType.device_control,
            description="Unlock front door",
            parameters={"device_id": "lock.front_door", "state": "unlock"},
            risk_level=RiskLevel.high,
            requires_confirmation=True,
            proposed_at=datetime.now(timezone.utc),
        )

        decision = self.service.decide(action)

        assert decision.verdict == DecisionVerdict.approved
        assert action.risk_level == RiskLevel.high
        assert action.requires_confirmation is True
