# app/main.py

from fastapi import FastAPI, Request
import uuid
from app.config.settings import get_settings
from app.config.logging import configure_logging
from app.core.context import correlation_id_ctx, tenant_id_ctx
from app.api.routers.health import router as health_router
import logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
)


logger = logging.getLogger(__name__)

@app.middleware("http")
async def context_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    tenant_id = request.headers.get("X-Tenant-ID", "public")

    correlation_id_ctx.set(correlation_id)
    tenant_id_ctx.set(tenant_id)

    logger.info(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"Completed request with status {response.status_code}")

    response.headers["X-Correlation-ID"] = correlation_id
    return response


app.include_router(health_router)
