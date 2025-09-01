# app/routers/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import uuid

from ..db import get_session
from ..models import SearchLog, Account, Subscription

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session)
):
    """Get dashboard statistics"""
    tenant_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    
    # Total businesses
    total_businesses = await session.scalar(
        select(func.count(Account.id)).where(Account.tenant_id == tenant_id)
    )
    
    # Active subscriptions
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.tenant_id == tenant_id,
            Subscription.status == 'active'
        )
    )
    
    # Searches today
    today_searches = await session.scalar(
        select(func.count(SearchLog.id)).where(
            SearchLog.tenant_id == tenant_id,
            SearchLog.created_at >= datetime.now().replace(hour=0, minute=0)
        )
    )
    
    # MRR calculation
    mrr = await session.scalar(
        select(func.sum(Subscription.amount_cents)).where(
            Subscription.tenant_id == tenant_id,
            Subscription.status == 'active'
        )
    ) or 0
    
    return {
        "total_businesses": total_businesses,
        "active_subscriptions": active_subs,
        "searches_today": today_searches,
        "mrr_cents": mrr,
        "mrr_dollars": mrr / 100
    }

    