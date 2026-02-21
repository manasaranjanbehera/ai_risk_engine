"""Events API router: POST /events (idempotent), GET /events/{event_id}."""

from typing import Annotated, Optional, Union

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse

from app.api.dependencies import get_event_service, get_tenant_id
from app.application.event_service import EventService
from app.domain.exceptions import DomainError, DomainValidationError
from app.domain.schemas.event import (
    ComplianceEventCreateRequest,
    EventResponse,
    RiskEventCreateRequest,
)

router = APIRouter()

IDEMPOTENCY_TTL = 300  # 5 minutes


def _idempotency_cache_key(tenant_id: str, key: str) -> str:
    return f"idempotency:{tenant_id}:{key}"


@router.post("/", response_model=EventResponse)
async def create_event(
    request: Request,
    body: Union[RiskEventCreateRequest, ComplianceEventCreateRequest],
    x_idempotency_key: Annotated[Optional[str], Header(alias="X-Idempotency-Key")] = None,
    tenant_id: Annotated[str, Depends(get_tenant_id)] = ...,
    event_service: Annotated[EventService, Depends(get_event_service)] = ...,
):
    """Create event (risk or compliance). Idempotent via X-Idempotency-Key."""
    if not x_idempotency_key or not x_idempotency_key.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "X-Idempotency-Key header is required"},
        )
    cache_key = _idempotency_cache_key(tenant_id, x_idempotency_key.strip())
    redis = event_service._redis
    cached = await redis.get_cache(cache_key)
    if cached:
        return Response(content=cached, media_type="application/json")
    try:
        # Use tenant_id from header (request state)
        if isinstance(body, RiskEventCreateRequest):
            req = RiskEventCreateRequest(
                tenant_id=tenant_id,
                risk_score=body.risk_score,
                category=body.category,
                metadata=body.metadata,
                version=body.version,
            )
            response = await event_service.create_risk_event(tenant_id, req)
        else:
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


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)] = ...,
    event_service: Annotated[EventService, Depends(get_event_service)] = ...,
):
    """Get event by ID (tenant-scoped)."""
    event = await event_service.get_event(tenant_id, event_id)
    if event is None:
        return JSONResponse(status_code=404, content={"detail": "Event not found"})
    return event
