"""Tests for POST /compliance: valid payload, validation failure, idempotency."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client(app_with_overrides):
    transport = ASGITransport(app=app_with_overrides)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def tenant_headers():
    return {"X-Tenant-ID": "test-tenant"}


@pytest.mark.asyncio
async def test_compliance_valid_payload_returns_200(client: AsyncClient, tenant_headers):
    """POST /compliance with valid ComplianceEventCreateRequest returns 200."""
    headers = {**tenant_headers, "X-Idempotency-Key": "comp-key-1"}
    body = {
        "tenant_id": "test-tenant",
        "version": "1.0",
        "regulation_ref": "GDPR",
        "compliance_type": "audit",
    }
    r = await client.post("/compliance/", json=body, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "event_id" in data
    assert data["tenant_id"] == "test-tenant"
    assert data["status"] == "created"


@pytest.mark.asyncio
async def test_compliance_validation_failure_returns_422(client: AsyncClient, tenant_headers):
    """POST /compliance with invalid body (e.g. empty version) returns 422."""
    headers = {**tenant_headers, "X-Idempotency-Key": "comp-key-422"}
    body = {"tenant_id": "test-tenant", "version": ""}
    r = await client.post("/compliance/", json=body, headers=headers)
    assert r.status_code == 422
    assert "detail" in r.json()


@pytest.mark.asyncio
async def test_compliance_idempotency_returns_cached(client: AsyncClient, tenant_headers):
    """Second POST /compliance with same idempotency key returns same response."""
    headers = {**tenant_headers, "X-Idempotency-Key": "comp-key-idem"}
    body = {"tenant_id": "test-tenant", "version": "1.0"}
    r1 = await client.post("/compliance/", json=body, headers=headers)
    r2 = await client.post("/compliance/", json=body, headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["event_id"] == r2.json()["event_id"]


@pytest.mark.asyncio
async def test_compliance_missing_idempotency_key_returns_400(client: AsyncClient, tenant_headers):
    """POST /compliance without X-Idempotency-Key returns 400."""
    body = {"tenant_id": "test-tenant", "version": "1.0"}
    r = await client.post("/compliance/", json=body, headers=tenant_headers)
    assert r.status_code == 400
