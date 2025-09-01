# app/routers/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, String
from typing import Optional
import uuid

from ..db import get_session
from ..models import Account, SearchLog, SearchResult

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/")
async def search_businesses(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session)
):
    """Search for businesses by name, description, or attributes"""
    
    # Log the search
    search_log = SearchLog(
        tenant_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        search_query=q,
        result_count=0
    )
    session.add(search_log)
    
    # Build search query
    search_term = f"%{q}%"
    query = select(Account).where(
        Account.tenant_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    ).where(
        or_(
            Account.company_name.ilike(search_term),
            Account.description.ilike(search_term),
            func.cast(Account.attributes, String).ilike(search_term)
        )
    ).limit(limit)
    
    # Execute search
    result = await session.execute(query)
    businesses = result.scalars().all()
    
    # Update search log
    search_log.result_count = len(businesses)
    
    # Create search results
    for idx, business in enumerate(businesses):
        search_result = SearchResult(
            search_log_id=search_log.id,
            account_id=business.id,
            position=idx + 1,
            score=100 - (idx * 5)
        )
        session.add(search_result)
    
    await session.commit()
    
    return {
        "search_id": str(search_log.id),
        "query": q,
        "result_count": len(businesses),
        "results": [
            {
                "id": str(business.id),
                "name": business.company_name or "Unknown",
                "description": business.description,
                "address": f"{business.bus_address_1}, {business.bus_city}, {business.bus_state}" if business.bus_address_1 else None,
                "phone": business.phone,
                "website": business.website,
                "lat": float(business.lat) if business.lat else None,
                "lng": float(business.lng) if business.lng else None,
                "attributes": business.attributes or {}
            }
            for business in businesses
        ]
    }

@router.get("/all")
async def get_all_businesses(
    session: AsyncSession = Depends(get_session)
):
    """Get all businesses for testing"""
    query = select(Account).where(
        Account.tenant_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    ).limit(30)
    
    result = await session.execute(query)
    businesses = result.scalars().all()
    
    return {
        "total": len(businesses),
        "businesses": [
            {
                "name": b.company_name,
                "address": f"{b.bus_address_1}, {b.bus_city}" if b.bus_address_1 else "No address",
                "description": b.description[:100] if b.description else None
            }
            for b in businesses
        ]
    }

