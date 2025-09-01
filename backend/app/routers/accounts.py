# app/routers/accounts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from ..db import get_session
from ..models import Account, Subscription, Category
from ..schemas import AccountResponse, AccountCreate, AccountUpdate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """List all business accounts"""
    query = select(Account).where(
        Account.tenant_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    ).offset(skip).limit(limit)
    
    result = await session.execute(query)
    accounts = result.scalars().all()
    
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific business account"""
    query = select(Account).where(Account.id == account_id)
    result = await session.execute(query)
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account

@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new business account"""
    db_account = Account(
        tenant_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        **account.dict()
    )
    session.add(db_account)
    await session.commit()
    await session.refresh(db_account)
    
    return db_account

@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    updates: AccountUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a business account"""
    query = select(Account).where(Account.id == account_id)
    result = await session.execute(query)
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(account, key, value)
    
    await session.commit()
    await session.refresh(account)
    
    return account

