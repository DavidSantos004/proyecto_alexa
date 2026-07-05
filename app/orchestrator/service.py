from app.orchestrator.domain.decision import DecisionVerdict, OrchestratorDecision
from app.orchestrator.domain.proposed_action import ProposedAction


class OrchestratorService:
    """
    Núcleo de decisión del sistema.

    Por ahora (Sprint 1) aprueba TODAS las acciones automáticamente.
    Esta decisión es TEMPORAL y está documentada: en sprints futuros
    se incorporarán rules engines, análisis de riesgo, y confirmación
    por voz/interfaz antes de decidir.
    """

    def decide(self, action: ProposedAction) -> OrchestratorDecision:
        return OrchestratorDecision(
            action_id=action.action_id,
            verdict=DecisionVerdict.approved,
            reason="Temporary auto-approval: all actions are approved in Sprint 1. "
            "Risk level and confirmation requirements are parsed but not yet enforced.",
        )
