from fastapi import FastAPI

app = FastAPI(
    title="JARVIS OS",
    description="Personal Intelligence Operating System API",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok"}
