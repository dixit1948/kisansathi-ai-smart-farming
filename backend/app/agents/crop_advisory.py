"""
Crop Advisory Agent — RAG-backed farming guidance.
Cites source+section in every response.
"""
import time
import structlog
from app.agents.schemas import AgentOutput, Source
from app.core.granite import get_granite_client
from app.rag.vector_store import get_vector_store

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are KisanSathi's Crop Advisory expert. You help Indian farmers with:
- Crop-specific cultivation practices
- Seed varieties and their suitability
- Fertiliser schedules (NPK, micronutrients)
- Sowing and harvest windows
- Government advisories and schemes

Rules:
1. ALWAYS cite the source document, section and page number at the end.
2. Provide specific, actionable advice (not vague).
3. Mention if advice is general or location-specific.
4. If you don't know, say "Please consult your local KVK agri officer."
5. Never recommend chemical doses not found in your source documents.
6. Keep answer under 300 words, plain language, numbered steps.

Context from knowledge base:
{context}

User query: {query}
Farmer's language preference: {language}

Respond in {language}. Be concise and practical."""


async def run_crop_advisory_agent(
    query: str,
    language: str = "en",
    crop: str = None,
    farm_context: dict = None,
) -> AgentOutput:
    start = time.time()
    granite = get_granite_client()
    vs = get_vector_store()

    # RAG retrieval
    chunks = await vs.retrieve(query, n_results=4, crop_filter=crop)
    context = "\n\n".join([f"[{c['metadata'].get('source', 'Unknown')}]\n{c['text']}" for c in chunks])
    sources = [
        Source(
            title=c["metadata"].get("source", "Unknown"),
            section=c["metadata"].get("topic"),
            page=c["metadata"].get("page"),
            is_sample=c["metadata"].get("is_sample", False),
        )
        for c in chunks
    ]

    # Inject farm context if available
    farm_str = ""
    if farm_context:
        farm_str = f"\nFarm details: {farm_context.get('soil_type', 'unknown')} soil, {farm_context.get('irrigation_type', 'unknown')} irrigation, {farm_context.get('area', '')} ha."

    prompt = SYSTEM_PROMPT.format(
        context=context or "No specific documents found. Provide general guidance and recommend local KVK.",
        query=query + farm_str,
        language=language,
    )

    result = await granite.generate(prompt, mock_key="crop_advisory", max_tokens=600, temperature=0.2)

    return AgentOutput(
        agent_name="crop_advisory",
        answer=result["text"],
        confidence=0.85 if chunks else 0.5,
        sources=sources,
        tool_calls=["rag_retrieval"],
        latency_ms=(time.time() - start) * 1000,
        is_mock=result["is_mock"],
    )
