"""FastAPI dependency injection: DB session, Redis, EventService, tenant."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.event_service import EventService
from app.infrastructure.cache.redis_client import RedisClient
from app.infrastructure.database.session import get_db

_redis_client: RedisClient | None = None


def get_redis_client() -> RedisClient:
    """Return singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


async def get_db_session():
    """Yield async DB session (from infrastructure)."""
    async for session in get_db():
        yield session


async def get_event_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[RedisClient, Depends(get_redis_client)],
) -> EventService:
    """Build EventService with injected DB session and Redis client."""
    return EventService(db=session, redis=redis)


def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request.state (set by middleware)."""
    return request.state.tenant_id
