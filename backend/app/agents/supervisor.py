"""
LangGraph Supervisor — classifies intent, routes to agents in parallel, merges response.
"""
import asyncio
import time
import uuid
from typing import Optional
import structlog
from app.agents.schemas import AgentOutput, SupervisorOutput, Source
from app.agents.crop_advisory import run_crop_advisory_agent
from app.agents.weather_irrigation import run_weather_irrigation_agent
from app.agents.pest_disease import run_pest_disease_agent
from app.agents.market_insights import run_market_insights_agent
from app.core.granite import get_granite_client
from app.core.config import settings

logger = structlog.get_logger(__name__)

INTENTS = ["advisory", "weather", "disease_photo", "market", "onboarding", "general"]

INTENT_CLASSIFIER_PROMPT = """Classify the farmer's message into ONE of these intents:
- advisory: crop planting, fertiliser, sowing, harvesting, cultivation practices
- weather: weather forecast, rain, temperature, irrigation timing
- disease_photo: leaf scan, disease, pest, insect, plant sick, photo analysis
- market: price, mandi, sell, rate, commodity price
- onboarding: registration, setup, language preference
- general: greeting, thanks, other

Message: "{query}"
Language hint: {language}

Reply with ONLY the intent word, nothing else."""


async def classify_intent(query: str, language: str = "en", has_image: bool = False) -> str:
    """Fast intent classification."""
    if has_image:
        return "disease_photo"

    # Quick keyword matching (fast path)
    query_lower = query.lower()
    if any(w in query_lower for w in ["weather", "rain", "temperature", "irrigation", "water", "मौसम", "weather", "પાણી"]):
        return "weather"
    if any(w in query_lower for w in ["price", "mandi", "sell", "rate", "market", "भाव", "ભાવ", "बाजार"]):
        return "market"
    if any(w in query_lower for w in ["disease", "pest", "sick", "leaf", "insect", "बीमारी", "रोग", "રોગ"]):
        return "disease_photo"

    granite = get_granite_client()
    if settings.USE_MOCK_LLM:
        return "advisory"

    result = await granite.generate(
        INTENT_CLASSIFIER_PROMPT.format(query=query, language=language),
        max_tokens=10, temperature=0.0,
    )
    intent = result["text"].strip().lower()
    return intent if intent in INTENTS else "advisory"


def _detect_language(text: str) -> str:
    """Simple language detection by Unicode ranges."""
    gujarati_count = sum(1 for c in text if "\u0A80" <= c <= "\u0AFF")
    devanagari_count = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    if gujarati_count > 3:
        return "gu"
    if devanagari_count > 3:
        return "hi"
    return "en"


async def run_supervisor(
    query: str,
    language: Optional[str] = None,
    image_path: Optional[str] = None,
    image_base64: Optional[str] = None,
    farm_context: Optional[dict] = None,
    crop: Optional[str] = None,
) -> SupervisorOutput:
    """
    Main entry point. Classifies intent, runs relevant agents (parallel where independent),
    merges into one answer in the farmer's language.
    """
    start = time.time()
    trace_id = str(uuid.uuid4())
    has_image = bool(image_path or image_base64)

    # Auto-detect language if not provided
    if not language:
        language = _detect_language(query)

    intent = await classify_intent(query, language, has_image)
    logger.info("Supervisor intent classified", intent=intent, trace_id=trace_id, mock=settings.USE_MOCK_LLM)

    # ── Route to agents ───────────────────────────────────────────────────────
    agent_tasks = []
    agent_names = []

    if intent == "disease_photo":
        agent_tasks.append(run_pest_disease_agent(image_path=image_path, image_base64=image_base64, crop=crop, language=language))
        agent_names.append("pest_disease")
    elif intent == "weather":
        lat = farm_context.get("latitude", 21.17) if farm_context else 21.17
        lon = farm_context.get("longitude", 72.83) if farm_context else 72.83
        soil = farm_context.get("soil_type", "loam") if farm_context else "loam"
        irr = farm_context.get("irrigation_type", "drip") if farm_context else "drip"
        agent_tasks.append(run_weather_irrigation_agent(lat=lat, lon=lon, soil_type=soil, irrigation_type=irr, crop=crop, language=language))
        agent_names.append("weather_irrigation")
    elif intent == "market":
        agent_tasks.append(run_market_insights_agent(crop=crop or "cotton", language=language))
        agent_names.append("market_insights")
    else:
        # Advisory or general: run crop advisory + weather in parallel
        agent_tasks.append(run_crop_advisory_agent(query=query, language=language, crop=crop, farm_context=farm_context))
        agent_names.append("crop_advisory")
        # Also fetch weather context for advisory
        if farm_context and farm_context.get("latitude"):
            agent_tasks.append(run_weather_irrigation_agent(
                lat=farm_context["latitude"], lon=farm_context["longitude"],
                soil_type=farm_context.get("soil_type", "loam"),
                irrigation_type=farm_context.get("irrigation_type", "drip"),
                crop=crop, language=language,
            ))
            agent_names.append("weather_irrigation")

    # Run agents in parallel
    agent_outputs: list[AgentOutput] = await asyncio.gather(*agent_tasks, return_exceptions=False)

    # Collect results
    all_sources: list[Source] = []
    for out in agent_outputs:
        all_sources.extend(out.sources)

    # Merge answer
    if len(agent_outputs) == 1:
        final_answer = agent_outputs[0].answer
    else:
        # Ask Granite to merge multiple agent answers coherently
        merge_prompt = f"""Merge these farming advice sections into ONE clear, concise response in {language}.
Keep the most actionable advice. No repetition. Max 400 words.
Add a brief intro and end with "🙏 For more help, type your question."

Section 1 ({agent_names[0]}):
{agent_outputs[0].answer}

Section 2 ({agent_names[1]}):
{agent_outputs[1].answer}"""

        granite = get_granite_client()
        merge_result = await granite.generate(merge_prompt, mock_key="general", max_tokens=500, temperature=0.2)
        final_answer = merge_result["text"]

    total_latency = (time.time() - start) * 1000
    is_mock = any(o.is_mock for o in agent_outputs)

    logger.info("Supervisor completed", intent=intent, agents=agent_names, latency_ms=round(total_latency), trace_id=trace_id)

    return SupervisorOutput(
        answer=final_answer,
        intent=intent,
        language=language,
        agents_used=agent_names,
        all_sources=all_sources,
        total_latency_ms=total_latency,
        is_mock=is_mock,
        trace_id=trace_id,
        agent_outputs=list(agent_outputs),
    )
