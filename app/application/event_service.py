"""Event application service — orchestrates event creation and retrieval."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.event import EventStatus
from app.domain.schemas.event import (
    ComplianceEventCreateRequest,
    EventResponse,
    RiskEventCreateRequest,
)
from app.domain.validators.event_validator import (
    validate_compliance_event_create_request,
    validate_risk_event_create_request,
)

from app.infrastructure.cache.redis_client import RedisClient

EVENT_CACHE_PREFIX = "event:"
EVENT_CACHE_TTL = 300  # 5 minutes


class EventService:
    """Orchestrates event creation and retrieval; uses Redis for storage (no DB events table)."""

    def __init__(self, db: AsyncSession, redis: RedisClient) -> None:
        self._db = db
        self._redis = redis

    async def create_risk_event(
        self,
        tenant_id: str,
        request: RiskEventCreateRequest,
    ) -> EventResponse:
        """Validate and create a risk event; store in Redis and return EventResponse."""
        validate_risk_event_create_request(request)
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        response = EventResponse(
            event_id=event_id,
            tenant_id=tenant_id,
            status=EventStatus.CREATED,
            created_at=now,
            metadata=request.metadata,
            version=request.version,
        )
        key = f"{EVENT_CACHE_PREFIX}{tenant_id}:{event_id}"
        await self._redis.set_cache(key, response.model_dump_json(), ttl=EVENT_CACHE_TTL)
        return response

    async def create_compliance_event(
        self,
        tenant_id: str,
        request: ComplianceEventCreateRequest,
    ) -> EventResponse:
        """Validate and create a compliance event; store in Redis and return EventResponse."""
        validate_compliance_event_create_request(request)
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        response = EventResponse(
            event_id=event_id,
            tenant_id=tenant_id,
            status=EventStatus.CREATED,
            created_at=now,
            metadata=request.metadata,
            version=request.version,
        )
        key = f"{EVENT_CACHE_PREFIX}{tenant_id}:{event_id}"
        await self._redis.set_cache(key, response.model_dump_json(), ttl=EVENT_CACHE_TTL)
        return response

    async def get_event(self, tenant_id: str, event_id: str) -> Optional[EventResponse]:
        """Retrieve event by tenant_id and event_id from Redis."""
        key = f"{EVENT_CACHE_PREFIX}{tenant_id}:{event_id}"
        raw = await self._redis.get_cache(key)
        if not raw:
            return None
        return EventResponse.model_validate_json(raw)
