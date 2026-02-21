"""Compliance API router: POST /compliance (idempotent)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Response
from fastapi.responses import JSONResponse

from app.api.dependencies import get_event_service, get_tenant_id
from app.application.event_service import EventService
from app.domain.exceptions import DomainError, DomainValidationError
from app.domain.schemas.event import ComplianceEventCreateRequest, EventResponse

router = APIRouter()

IDEMPOTENCY_TTL = 300


def _idempotency_cache_key(tenant_id: str, key: str) -> str:
    return f"idempotency:compliance:{tenant_id}:{key}"


@router.post("/", response_model=EventResponse)
async def create_compliance_event(
    body: ComplianceEventCreateRequest,
    x_idempotency_key: Annotated[Optional[str], Header(alias="X-Idempotency-Key")] = None,
    tenant_id: Annotated[str, Depends(get_tenant_id)] = ...,
    event_service: Annotated[EventService, Depends(get_event_service)] = ...,
):
    """Create compliance event. Idempotent via X-Idempotency-Key."""
    if not x_idempotency_key or not x_idempotency_key.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "X-Idempotency-Key header is required"},
        )
    key = x_idempotency_key.strip()
    cache_key = _idempotency_cache_key(tenant_id, key)
    redis = event_service._redis
    cached = await redis.get_cache(cache_key)
    if cached:
        return Response(content=cached, media_type="application/json")
    try:
        req = ComplianceEventCreateRequest(
            tenant_id=tenant_id,
            regulation_ref=body.regulation_ref,
            compliance_type=body.compliance_type,
            metadata=body.metadata,
            version=body.version,
        )
        response = await event_service.create_compliance_event(tenant_id, req)
    except DomainValidationError as e:
        return JSONResponse(status_code=422, content={"detail": e.message})
    except DomainError as e:
        return JSONResponse(status_code=400, content={"detail": e.message})
    response_json = response.model_dump_json()
    await redis.set_cache(cache_key, response_json, ttl=IDEMPOTENCY_TTL)
    return Response(content=response_json, media_type="application/json")
