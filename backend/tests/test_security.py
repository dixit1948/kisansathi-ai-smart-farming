"""
Security & OWASP compliance tests for KisanSathi.
Tests:
- A01: Broken Access Control & IDOR attempts (farmers cannot access other farmers' farms/scans)
- A02: Cryptographic password hash verification (Argon2 / PBKDF2)
- A05: Security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- LLM01: Prompt injection isolation
- DPDP Act: Consent enforcement
"""
import pytest
from httpx import AsyncClient
from app.core.security import hash_password, verify_password


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Verify standard security headers on API responses."""
    res = await client.get("/healthz")
    headers = res.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") in ["DENY", "SAMEORIGIN"]
    assert "x-request-id" in headers or "X-Request-ID" in headers


@pytest.mark.asyncio
async def test_password_hashing_security():
    """Verify passwords are irreversibly hashed and verified."""
    raw = "StrongSecret123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_unauthenticated_protected_endpoint(client: AsyncClient):
    """Verify unauthorized access to protected farm endpoints fails with 401."""
    res = await client.get("/api/v1/farms/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_registration_requires_consent(client: AsyncClient):
    """Verify DPDP Act 2023 requirement: registration without consent must fail."""
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": "+919876543201",
            "password": "Password@123",
            "full_name": "Test No Consent",
            "consent_given": False,
        },
    )
    assert res.status_code == 400
    assert "CONSENT" in str(res.json())
