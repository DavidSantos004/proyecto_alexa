from fastapi import FastAPI

from app.api.router import router as api_router
from app.orchestrator.router import router as orchestrator_router

app = FastAPI(
    title="JARVIS OS",
    description="Personal Intelligence Operating System API",
    version="0.1.0",
)

app.include_router(orchestrator_router)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
