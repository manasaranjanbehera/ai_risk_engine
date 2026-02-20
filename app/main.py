# app/main.py

import logging
import uuid

from fastapi import FastAPI, Request

from app.api.routers.health import router as health_router
from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.core.context import correlation_id_ctx, tenant_id_ctx

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
