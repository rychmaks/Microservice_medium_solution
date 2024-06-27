"""This module is used for announcement of database tables for adjustment service."""

from datetime import datetime

from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    DECIMAL,
    DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

metadata = MetaData()
Adjustments = Table(
    "adjustments",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("project_uuid", UUID(as_uuid=True), nullable=False),
    Column("price_group_uuid", UUID(as_uuid=True), nullable=False),
    Column("bu_uuid", UUID(as_uuid=True), nullable=True),
    Column("product_uuid", UUID(as_uuid=True), nullable=True),
    Column("adjustment_value", DECIMAL, nullable=True),
    Column("tier_override", JSONB, nullable=True),
    Column("comment", String, nullable=False),
    Column("user", String, nullable=False),
    Column("user_full_name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)

models = (Adjustments,)
