import os

# Force MOCK_LLM and SQLite for tests before application modules are imported
os.environ["USE_MOCK_LLM"] = "true"
os.environ["SQLITE_FALLBACK"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-long-minimum!"

from typing import AsyncGenerator  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
import pytest_asyncio  # noqa: E402

from app.main import app  # noqa: E402
from app.core.database import Base, engine, AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.models.farmer import FarmerProfile  # noqa: E402
from app.models.farm import Farm, SoilType, IrrigationType  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create all tables in test database once per session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    """Provide a transactional database session."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client bound to FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def demo_farmer(db_session) -> User:
    """Seed a test farmer user."""
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.phone == "+919876543210"))
    existing = res.scalar_one_or_none()
    if existing:
        return existing

    user = User(
        phone="+919876543210",
        hashed_password=hash_password("Demo@1234"),
        role=UserRole.FARMER,
        preferred_language="gu",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    profile = FarmerProfile(user_id=user.id, full_name="Arjun Bhai Patel", district="Surat", taluka="Bardoli")
    db_session.add(profile)
    await db_session.commit()

    farm = Farm(
        farmer_profile_id=profile.id,
        name="Test Cotton Farm",
        latitude=21.12,
        longitude=73.11,
        area_hectares=3.5,
        soil_type=SoilType.BLACK,
        irrigation_type=IrrigationType.DRIP,
    )
    db_session.add(farm)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def demo_officer(db_session) -> User:
    """Seed a test officer user."""
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.email == "officer@kvk.gov.in"))
    existing = res.scalar_one_or_none()
    if existing:
        return existing

    officer = User(
        email="officer@kvk.gov.in",
        hashed_password=hash_password("Demo@1234"),
        role=UserRole.OFFICER,
        preferred_language="en",
        is_active=True,
    )
    db_session.add(officer)
    await db_session.commit()
    await db_session.refresh(officer)
    return officer
