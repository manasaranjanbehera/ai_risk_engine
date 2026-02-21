# app/infrastructure/database/models.py

import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column(String, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

    is_deleted = Column(Boolean, default=False)



class TestEvent(BaseModel):
    __tablename__ = "test_events"

    name = Column(String)
    idempotency_key = Column(String, unique=True)