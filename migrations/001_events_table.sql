-- Events table for DB-backed event store (application boundary, status RECEIVED).
-- Run this against your database to enable DbEventRepository.
-- Requires: BaseModel columns (id, tenant_id, created_at, updated_at, created_by, updated_by, is_deleted).

CREATE TABLE IF NOT EXISTS events (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    tenant_id varchar NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz,
    created_by varchar,
    updated_by varchar,
    is_deleted boolean DEFAULT false,
    event_id varchar NOT NULL,
    correlation_id varchar NOT NULL,
    status varchar NOT NULL DEFAULT 'received',
    event_type varchar NOT NULL,
    metadata jsonb,
    version varchar NOT NULL DEFAULT '1.0'
);

CREATE INDEX IF NOT EXISTS idx_events_tenant_id ON events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_tenant_event_id ON events(tenant_id, event_id);

COMMENT ON TABLE events IS 'Persisted domain events at application boundary (status RECEIVED).';
