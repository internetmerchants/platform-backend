# app/models.py
from sqlalchemy import String, Text, TIMESTAMP, Boolean, Integer, DECIMAL, JSON, ForeignKey, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .db import Base
import uuid
from datetime import datetime
from typing import Optional, List

class Tenant(Base):
    __tablename__ = "tenants"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    tenant_type: Mapped[Optional[str]] = mapped_column(String(50))
    subscription_tier: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    accounts: Mapped[List["Account"]] = relationship(back_populates="tenant")
    categories: Mapped[List["Category"]] = relationship(back_populates="tenant")

class Account(Base):
    __tablename__ = "accounts"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    email_address: Mapped[str] = mapped_column(Text, nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location
    lat: Mapped[Optional[float]] = mapped_column(DECIMAL(9,6))
    lng: Mapped[Optional[float]] = mapped_column(DECIMAL(9,6))
    
    # JSON attributes for search
    attributes: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    
    # Address
    bus_address_1: Mapped[Optional[str]] = mapped_column(Text)
    bus_city: Mapped[Optional[str]] = mapped_column(Text)
    bus_state: Mapped[Optional[str]] = mapped_column(Text)
    bus_zip: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="accounts")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="account")
    search_results: Mapped[List["SearchResult"]] = relationship(back_populates="account")

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    tenant: Mapped["Tenant"] = relationship(back_populates="categories")

class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    search_query: Mapped[str] = mapped_column(Text, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    search_results: Mapped[List["SearchResult"]] = relationship(back_populates="search_log")

class SearchResult(Base):
    __tablename__ = "search_results"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_log_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("search_logs.id"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(DECIMAL(6,2))
    was_clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    search_log: Mapped["SearchLog"] = relationship(back_populates="search_results")
    account: Mapped["Account"] = relationship(back_populates="search_results")

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("products.id"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending')
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    account: Mapped["Account"] = relationship(back_populates="subscriptions")

    