"""Database setup — async SQLAlchemy with SQLite fallback."""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class Base(DeclarativeBase):
    pass


def _make_engine():
    url = settings.effective_database_url
    kwargs = {}
    if settings.is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_async_engine(url, echo=settings.DEBUG, future=True, **kwargs)


engine = _make_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables (used for SQLite dev; production uses Alembic)."""
    if settings.is_sqlite:
        async with engine.begin() as conn:
            from app.models import user, farmer, farm, conversation, scan, alert, market, knowledge, trace  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite tables created")
    else:
        # In production, Alembic manages schema
        logger.info("PostgreSQL — skipping auto-create; use 'alembic upgrade head'")
    # Verify connectivity
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connected", url=settings.effective_database_url.split("@")[-1])
