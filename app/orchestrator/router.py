from fastapi import APIRouter

from app.orchestrator.domain.proposed_action import ProposedAction
from app.orchestrator.service import OrchestratorService

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])
service = OrchestratorService()


@router.post("/propose")
def propose(action: ProposedAction):
    return service.decide(action)
