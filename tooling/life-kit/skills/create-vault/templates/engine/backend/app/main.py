from __future__ import annotations

from fastapi import FastAPI

from .api.health import router as health_router
from .config import settings

app = FastAPI(title=f"{settings.project_name} engine")
app.include_router(health_router)


@app.get("/")
async def root() -> dict:
    return {"engine": settings.project_name, "docs": "/docs", "health": "/health"}
