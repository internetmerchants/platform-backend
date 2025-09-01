# app/routers/search.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy import String  # Add this to the imports
from typing import List, Optional
from datetime import datetime
import uuid

from ..db import get_session
from ..models import Account, SearchLog, SearchResult, Category
from ..schemas import SearchRequest, SearchResponse, BusinessResult

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search_businesses(
    request: SearchRequest,
    session: AsyncSession = Depends(get_session)
):
    """Search for businesses based on query and filters"""
    
    # Create search log entry
    search_log = SearchLog(
        tenant_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),  # Charleston tenant
        search_query=request.query,
        user_id=request.user_id
    )
    session.add(search_log)
    
    # Build search query
    query = select(Account).where(
        Account.tenant_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    )
    
    # Text search
    if request.query:
        search_term = f"%{request.query}%"
        query = query.where(
            or_(
                Account.company_name.ilike(search_term),
                Account.description.ilike(search_term),
                func.cast(Account.attributes, String).ilike(search_term)
            )
        )
    
    # Category filter
    if request.category_id:
        query = query.join(BusinessCategoryMapping).where(
            BusinessCategoryMapping.category_id == request.category_id
        )
    
    # Location filter (if lat/lng provided)
    if request.lat and request.lng and request.radius_km:
        # Simple distance calculation (for more accuracy, use PostGIS)
        query = query.where(
            func.sqrt(
                func.pow(Account.lat - request.lat, 2) + 
                func.pow(Account.lng - request.lng, 2)
            ) * 111 < request.radius_km  # Rough conversion to km
        )
    
    # Execute search
    result = await session.execute(query.limit(20))
    businesses = result.scalars().all()
    
    # Update search log with results
    search_log.result_count = len(businesses)
    
    # Create search results
    for idx, business in enumerate(businesses):
        search_result = SearchResult(
            search_log_id=search_log.id,
            account_id=business.id,
            position=idx + 1,
            score=100 - (idx * 5)  # Simple scoring
        )
        session.add(search_result)
    
    await session.commit()
    
    return SearchResponse(
        search_id=search_log.id,
        query=request.query,
        result_count=len(businesses),
        results=[
            BusinessResult(
                id=b.id,
                name=b.company_name,
                description=b.description,
                address=f"{b.bus_address_1}, {b.bus_city}, {b.bus_state}",
                phone=b.phone,
                website=b.website,
                lat=float(b.lat) if b.lat else None,
                lng=float(b.lng) if b.lng else None,
                attributes=b.attributes or {}
            )
            for b in businesses
        ]
    )

@router.get("/trending")
async def get_trending_searches(
    session: AsyncSession = Depends(get_session)
):
    """Get trending search terms"""
    query = select(
        SearchLog.search_query,
        func.count(SearchLog.id).label('count')
    ).where(
        SearchLog.tenant_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    ).group_by(
        SearchLog.search_query
    ).order_by(
        func.count(SearchLog.id).desc()
    ).limit(10)
    
    result = await session.execute(query)
    trends = result.all()
    
    return [
        {"query": trend[0], "count": trend[1]}
        for trend in trends
    ]
