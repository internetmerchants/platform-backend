# app/db.py
# PgBouncer setup is excellent for production - it handles connection pooling efficiently. 
# The code structure with async SQLAlchemy is modern and scalable.
    
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Settings(BaseSettings):
    # PgBouncer on 6432
    DB_NAME: str = "platform"
    DB_HOST: str = "127.0.0.1"

#   DB_PORT: int = 6432  # 6432 for PgBouncer
    DB_PORT: int = 5432  # 5432 for direct PostgreSQL

#   DB_USER: str = "platformuser"
#   DB_PASSWORD: str = "Cantgetin#999"

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "yourpass"

    # CORS origin for the frontend
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# IMPORTANT: disable asyncpg prepared-statement caches for PgBouncer (transaction mode)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        # disable prepared-stmt cache for PgBouncer
        # asyncpg caches prepared statements by default; turn it off for PgBouncer
        "statement_cache_size": 0,
        # some asyncpg builds also honor this (harmless if unknown)
        "prepared_statement_cache_size": 0,
    },
)

# Session factory
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for ORM models
class Base(DeclarativeBase):
    pass

# FastAPI dependency
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

