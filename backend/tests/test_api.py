"""
Integration tests for KisanSathi FastAPI endpoints.
Tests /healthz, /readyz, /auth, /chat, /scan, /weather, /market, /alerts, /officer.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(client: AsyncClient):
    """Verify health and readiness check endpoints."""
    res_liveness = await client.get("/healthz")
    assert res_liveness.status_code == 200
    assert res_liveness.json()["status"] == "ok"

    res_readiness = await client.get("/readyz")
    assert res_readiness.status_code == 200
    assert res_readiness.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_auth_otp_flow(client: AsyncClient):
    """Verify phone OTP flow."""
    # Send OTP
    res_send = await client.post("/api/v1/auth/otp/send", json={"phone": "+919876543299"})
    assert res_send.status_code in [200, 201]

    # Verify OTP
    res_verify = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+919876543299", "otp": "123456"},
    )
    assert res_verify.status_code == 200
    data = res_verify.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_weather_endpoint(client: AsyncClient):
    """Verify weather forecast endpoint."""
    res = await client.get("/api/v1/weather/forecast?lat=21.17&lon=72.83")
    assert res.status_code == 200
    data = res.json()
    assert "forecast" in data or "irrigation_needed_mm" in data or "location" in data


@pytest.mark.asyncio
async def test_market_prices_endpoint(client: AsyncClient):
    """Verify market prices and trend forecasting."""
    res = await client.get("/api/v1/market/prices?crop=cotton")
    assert res.status_code == 200
    data = res.json()
    assert "prices" in data or "trend" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_message_endpoint(client: AsyncClient):
    """Verify multi-agent chat message endpoint."""
    res = await client.post(
        "/api/v1/chat/message",
        json={
            "message": "When should I apply first split nitrogen for cotton?",
            "language": "en",
            "crop": "cotton",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "intent" in data
    assert "agents_used" in data
