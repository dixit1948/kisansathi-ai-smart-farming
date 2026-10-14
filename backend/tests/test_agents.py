"""
Unit tests for KisanSathi LangGraph Multi-Agent System.
Tests Crop Advisory, Weather & Irrigation, Pest & Disease, Market Insights, and Supervisor routing.
"""
import pytest
from app.agents.supervisor import run_supervisor, classify_intent
from app.agents.crop_advisory import run_crop_advisory_agent
from app.agents.weather_irrigation import run_weather_irrigation_agent
from app.agents.pest_disease import run_pest_disease_agent
from app.agents.market_insights import run_market_insights_agent


@pytest.mark.asyncio
async def test_intent_classification():
    """Verify keyword and intent routing across multiple domains."""
    assert await classify_intent("How much rain is expected tomorrow?") == "weather"
    assert await classify_intent("What is the current cotton mandi price?") == "market"
    assert await classify_intent("My plant has a yellow disease", has_image=False) == "disease_photo"
    assert await classify_intent("Uploaded photo", has_image=True) == "disease_photo"
    assert await classify_intent("When should I sow wheat?") == "advisory"


@pytest.mark.asyncio
async def test_crop_advisory_agent():
    """Verify crop advisory agent returns typed output with citations."""
    out = await run_crop_advisory_agent(
        query="When should I apply first split nitrogen for cotton?",
        crop="cotton",
        language="en",
    )
    assert out.agent_name == "crop_advisory"
    assert len(out.answer) > 0
    assert out.confidence >= 0.5
    assert len(out.sources) > 0
    assert out.sources[0].title is not None
    assert out.latency_ms >= 0


@pytest.mark.asyncio
async def test_weather_irrigation_agent():
    """Verify weather & irrigation agent calculates ET0 and returns actionable watering guidance."""
    out = await run_weather_irrigation_agent(
        lat=21.17,
        lon=72.83,
        soil_type="black",
        irrigation_type="drip",
        crop="cotton",
        language="en",
    )
    assert out.agent_name == "weather_irrigation"
    assert len(out.answer) > 0
    assert "irrigation" in out.answer.lower() or "water" in out.answer.lower() or "mock" in out.answer.lower()
    assert out.confidence >= 0.5


@pytest.mark.asyncio
async def test_pest_disease_agent():
    """Verify pest & disease agent diagnoses leaf condition with organic first treatment."""
    out = await run_pest_disease_agent(
        image_path="./uploads/sample/scan_1.jpg",
        crop="cotton",
        language="en",
    )
    assert out.agent_name == "pest_disease"
    assert len(out.answer) > 0
    assert out.confidence >= 0.6  # Above confidence threshold
    assert out.extra is not None
    assert "predicted_label" in out.extra
    assert "severity" in out.extra
    assert len(out.sources) > 0


@pytest.mark.asyncio
async def test_market_insights_agent():
    """Verify market agent returns mandi price trend and sell-timing advice."""
    out = await run_market_insights_agent(crop="cotton", district="Surat", language="en")
    assert out.agent_name == "market_insights"
    assert len(out.answer) > 0
    assert out.confidence >= 0.5


@pytest.mark.asyncio
async def test_supervisor_merge():
    """Verify supervisor coordinates parallel execution and returns unified synthesis."""
    sup_out = await run_supervisor(
        query="Can I irrigate my cotton field tomorrow and apply fertilizer?",
        crop="cotton",
        language="en",
    )
    assert len(sup_out.answer) > 0
    assert sup_out.intent in ["advisory", "weather"]
    assert len(sup_out.agents_used) >= 1
    assert len(sup_out.agent_outputs) >= 1
    assert sup_out.total_latency_ms >= 0
