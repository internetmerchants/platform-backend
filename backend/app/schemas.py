# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Existing Task schemas...

# Search schemas
class SearchRequest(BaseModel):
    query: str
    category_id: Optional[uuid.UUID] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = 10
    user_id: Optional[uuid.UUID] = None

class BusinessResult(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    attributes: Dict[str, Any]

class SearchResponse(BaseModel):
    search_id: uuid.UUID
    query: str
    result_count: int
    results: List[BusinessResult]

# Account schemas
class AccountBase(BaseModel):
    email_address: str
    company_name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    bus_address_1: Optional[str] = None
    bus_city: Optional[str] = None
    bus_state: Optional[str] = None
    bus_zip: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class AccountResponse(AccountBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Category schemas
class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

        