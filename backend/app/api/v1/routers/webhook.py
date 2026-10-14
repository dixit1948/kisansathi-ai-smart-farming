"""
WhatsApp Cloud API webhook handler.
GET: webhook verification (verify_token check)
POST: receive messages with X-Hub-Signature-256 HMAC verification + idempotency
"""
import hashlib
import hmac
import json
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import structlog

from app.core.config import settings
from app.agents.supervisor import run_supervisor

logger = structlog.get_logger(__name__)
router = APIRouter()

# In-memory idempotency store (use Redis in production)
_processed_message_ids: set[str] = set()


@router.get("/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """WhatsApp webhook verification endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return PlainTextResponse(hub_challenge)
    raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "Invalid verify token."})


def _verify_hmac_signature(payload: bytes, signature_header: str) -> bool:
    """Verify X-Hub-Signature-256 HMAC on incoming webhook POST."""
    if not settings.WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not set — skipping HMAC verification (insecure!)")
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


async def _handle_whatsapp_message(message: dict, phone_number: str):
    """Process a single WhatsApp message and send reply."""
    try:
        import httpx
        msg_type = message.get("type", "text")
        msg_id = message.get("id", "")
        text = ""
        image_b64 = None

        if msg_type == "text":
            text = message.get("text", {}).get("body", "")
        elif msg_type == "image":
            # Download image and convert to base64
            image_id = message.get("image", {}).get("id")
            if image_id:
                try:
                    async with httpx.AsyncClient() as client:
                        # Get image URL from WhatsApp media API
                        media_resp = await client.get(
                            f"https://graph.facebook.com/v18.0/{image_id}",
                            headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
                        )
                        media_url = media_resp.json().get("url", "")
                        if media_url:
                            img_resp = await client.get(media_url, headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"})
                            import base64
                            image_b64 = base64.b64encode(img_resp.content).decode()
                            text = "Scan this leaf for disease"
                except Exception as e:
                    logger.error("Failed to download WhatsApp image", error=str(e))
        elif msg_type == "audio":
            text = "[Voice note received — transcription not available in this version]"
        else:
            text = message.get("text", {}).get("body", "Hello")

        if not text and not image_b64:
            return

        # Run supervisor
        result = await run_supervisor(query=text, image_base64=image_b64)
        reply_text = result.answer

        # Send reply via WhatsApp API
        if settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
                    headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": phone_number,
                        "type": "text",
                        "text": {"body": reply_text[:4096]},  # WhatsApp text limit
                    },
                    timeout=15.0,
                )
        else:
            logger.info("WhatsApp reply (dev — not sent)", to=phone_number, msg_id=msg_id, reply=reply_text[:200])

    except Exception as e:
        logger.error("WhatsApp message handler error", error=str(e), phone=phone_number, msg_id=msg_id)


@router.post("/whatsapp")
async def whatsapp_receive(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive WhatsApp webhook events."""
    # Verify signature
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_hmac_signature(body, sig):
        logger.warning("WhatsApp webhook HMAC verification failed")
        raise HTTPException(403, detail={"code": "INVALID_SIGNATURE", "message": "HMAC verification failed."})

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, detail={"code": "INVALID_JSON", "message": "Invalid JSON payload."})

    # Process messages
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                msg_id = message.get("id", "")
                phone_number = message.get("from", "")

                # Idempotency: skip already processed messages
                if msg_id in _processed_message_ids:
                    logger.info("Duplicate WhatsApp message — skipping", msg_id=msg_id)
                    continue
                _processed_message_ids.add(msg_id)
                # Keep store bounded
                if len(_processed_message_ids) > 10000:
                    _processed_message_ids.clear()

                background_tasks.add_task(_handle_whatsapp_message, message, phone_number)

    return {"status": "ok"}
