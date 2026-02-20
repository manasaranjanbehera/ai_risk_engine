# scripts/test_repository.py

import sys
from pathlib import Path

# Ensure project root is on the path when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from sqlalchemy import delete
from app.infrastructure.database.session import AsyncSessionLocal, engine, Base
from app.infrastructure.database.repository import AsyncRepository
from app.infrastructure.database.models import TestEvent

TEST_IDEMPOTENCY_KEY = "abc123"
TEST_TENANT_ID = "tenant_a"


async def test_repo():
    # Create tables (e.g. test_events) if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Clear existing test data so re-runs don't hit unique constraint
        await db.execute(
            delete(TestEvent).where(
                TestEvent.idempotency_key == TEST_IDEMPOTENCY_KEY,
                TestEvent.tenant_id == TEST_TENANT_ID,
            )
        )
        await db.commit()

        repo = AsyncRepository(TestEvent)

        event = TestEvent(
            tenant_id=TEST_TENANT_ID,
            name="event1",
            idempotency_key=TEST_IDEMPOTENCY_KEY,
        )

        await repo.create(db, event)

        result = await repo.get_by_id(db, event.id, TEST_TENANT_ID)
        print("Found:", result.name)

asyncio.run(test_repo())
