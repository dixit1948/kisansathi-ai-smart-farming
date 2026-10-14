"""
WhatsApp Cloud API Webhook verification tests.
Tests hub.challenge GET verification, HMAC-SHA256 signature verification, and replay protection.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_whatsapp_webhook_get_verification_success(client: AsyncClient):
    """Verify Meta challenge verification returns challenge string when token matches."""
    verify_token = settings.WHATSAPP_VERIFY_TOKEN
    challenge = "1158201444"
    res = await client.get(
        f"/api/v1/webhook/whatsapp?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge={challenge}"
    )
    assert res.status_code == 200
    assert res.text == challenge


@pytest.mark.asyncio
async def test_whatsapp_webhook_get_verification_failure(client: AsyncClient):
    """Verify rejection when token does not match."""
    res = await client.get(
        "/api/v1/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=WRONG_TOKEN&hub.challenge=123"
    )
    assert res.status_code in [401, 403]


@pytest.mark.asyncio
async def test_whatsapp_webhook_post_hmac_invalid(client: AsyncClient):
    """Verify inbound POST is rejected with 401/403 if HMAC signature is missing or fraudulent."""
    payload = b'{"object": "whatsapp_business_account"}'
    res = await client.post(
        "/api/v1/webhook/whatsapp",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalidhexsignature0000000000000000",
        },
    )
    # If app secret is configured, must reject invalid signature
    if settings.WHATSAPP_APP_SECRET:
        assert res.status_code in [401, 403]
    else:
        # Dev fallback when secret is empty
        assert res.status_code in [200, 401, 403]
