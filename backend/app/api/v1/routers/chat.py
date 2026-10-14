"""Chat router — SSE streaming + conversation history."""
import asyncio
import json
from typing import Optional, AsyncIterator
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.api.deps import get_optional_current_user, require_farmer
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.models.trace import AgentTrace
from app.agents.supervisor import run_supervisor

logger = structlog.get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = None
    crop: Optional[str] = None


@router.post("/message")
async def chat_message(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user),
):
    """Direct JSON chat endpoint invoking LangGraph Supervisor."""
    from app.services.farmer_service import get_farmer_context
    farm_context = None
    if user:
        farm_context = await get_farmer_context(user.id, db)
    result = await run_supervisor(
        query=req.message,
        language=req.language or (user.preferred_language if user else "en"),
        farm_context=farm_context,
        crop=req.crop,
    )
    return {
        "answer": result.answer,
        "intent": result.intent,
        "language": result.language,
        "agents_used": result.agents_used,
        "all_sources": [s.model_dump() for s in result.all_sources],
        "total_latency_ms": result.total_latency_ms,
        "is_mock": result.is_mock,
        "trace_id": result.trace_id,
    }


@router.post("/conversations")
async def create_conversation(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    conv = Conversation(user_id=user.id, language=user.preferred_language)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {"id": conv.id, "created_at": conv.created_at.isoformat()}


@router.get("/conversations")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
    limit: int = 20,
    offset: int = 0,
):
    result = await db.execute(
        select(Conversation).where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)
    )
    convs = result.scalars().all()
    return [{"id": c.id, "language": c.language, "created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat()} for c in convs]


@router.get("/conversations/{conv_id}/messages")
async def get_messages(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
    limit: int = 50,
    offset: int = 0,
):
    # Object-level authorization
    conv_res = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = conv_res.scalar_one_or_none()
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Conversation not found."})

    result = await db.execute(
        select(Message).where(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc()).limit(limit).offset(offset)
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id, "role": m.role.value, "content": m.content,
            "language": m.language, "sources": m.sources,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.post("/stream")
async def chat_stream(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    crop: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    """SSE streaming chat endpoint."""
    # Get or create conversation
    conv = None
    if conversation_id:
        res = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))
        conv = res.scalar_one_or_none()
    if not conv:
        conv = Conversation(user_id=user.id, language=language or user.preferred_language)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

    # Save user message
    user_msg = Message(
        conversation_id=conv.id, role=MessageRole.USER,
        content=message, language=language or user.preferred_language,
    )
    db.add(user_msg)
    await db.commit()

    # Handle image upload
    image_b64 = None
    if image and image.size and image.size > 0:
        from app.services.upload import process_image_upload
        image_b64 = await process_image_upload(image, user.id)

    # Get farm context
    from app.services.farmer_service import get_farmer_context
    farm_context = await get_farmer_context(user.id, db)

    async def event_generator() -> AsyncIterator[str]:
        try:
            # Run supervisor
            result = await run_supervisor(
                query=message,
                language=language or user.preferred_language,
                image_base64=image_b64,
                farm_context=farm_context,
                crop=crop,
            )

            # Stream answer word by word
            words = result.answer.split()
            for i, word in enumerate(words):
                data = json.dumps({"type": "token", "content": word + " "})
                yield f"data: {data}\n\n"
                if i % 5 == 0:
                    await asyncio.sleep(0.01)  # throttle slightly

            # Send sources
            sources_data = json.dumps({
                "type": "sources",
                "sources": [s.model_dump() for s in result.all_sources],
                "trace_id": result.trace_id,
                "is_mock": result.is_mock,
                "latency_ms": round(result.total_latency_ms),
            })
            yield f"data: {sources_data}\n\n"

            # Save assistant message
            assistant_msg = Message(
                conversation_id=conv.id, role=MessageRole.ASSISTANT,
                content=result.answer, language=result.language,
                sources=[s.model_dump() for s in result.all_sources],
                agent_trace_id=result.trace_id,
            )
            db.add(assistant_msg)

            # Save trace
            trace = AgentTrace(
                id=result.trace_id,
                conversation_id=conv.id,
                user_id=user.id,
                supervisor_intent=result.intent,
                agents_invoked=result.agents_used,
                agent_outputs=[o.model_dump() for o in result.agent_outputs],
                total_latency_ms=result.total_latency_ms,
                is_mock=result.is_mock,
            )
            db.add(trace)
            await db.commit()

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.error("Chat stream error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': 'Sorry, something went wrong. Please try again.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/traces/{trace_id}")
async def get_trace(
    trace_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    """Get agent trace for the demo Agent Trace view."""
    res = await db.execute(select(AgentTrace).where(AgentTrace.id == trace_id))
    trace = res.scalar_one_or_none()
    if not trace:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Trace not found."})
    # Only return own traces (or officer/admin can see any)
    if trace.user_id != user.id and user.role.value not in ("officer", "admin"):
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "Access denied."})
    return {
        "id": trace.id,
        "intent": trace.supervisor_intent,
        "agents_invoked": trace.agents_invoked,
        "agent_outputs": trace.agent_outputs,
        "total_latency_ms": trace.total_latency_ms,
        "is_mock": trace.is_mock,
        "created_at": trace.created_at.isoformat(),
    }
