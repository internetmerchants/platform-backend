# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from .db import engine, Base, get_session, settings
from .models import Account  # Import your models
# from .routers.tasks import router as tasks_router  # Comment out for now
from .routers import search
from .routers import agents

# Load environment variables from .env file
# Now your OPENAI_API_KEY will be available
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI(title="Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Changed this line
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def on_startup():
    # Create tables if missing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Platform API is running"}

@app.get("/ping")
async def ping():
    return {"ok": True}

app.include_router(search.router)
app.include_router(agents.router)

# Test endpoint to verify database connection
@app.get("/test-db")
async def test_db():
    async for session in get_session():
        try:
            # Try to query accounts
            result = await session.execute(select(Account).limit(1))
            account = result.scalar_one_or_none()
            return {
                "database": "connected",
                "sample_account": account.company_name if account else "No accounts found"
            }
        except Exception as e:
            return {"database": "error", "message": str(e)}
        break

