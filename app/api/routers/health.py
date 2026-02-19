# app/api/routers/health.py

from fastapi import APIRouter
from app.config.settings import get_settings

router = APIRouter()

@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.version,
    }
