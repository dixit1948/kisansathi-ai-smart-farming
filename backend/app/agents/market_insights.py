"""
Market Insights Agent — mandi prices, trend forecasting, sell-timing advice.
Uses Agmarknet API (if key provided) or sample CSV fallback.
"""
import time
from typing import Optional
import structlog
from app.agents.schemas import AgentOutput, Source
from app.core.config import settings
from app.core.granite import get_granite_client

logger = structlog.get_logger(__name__)

# Sample market data (Gujarat mandis) — clearly labelled as sample
SAMPLE_PRICES = {
    "cotton": [
        {"date": "2024-06-10", "mandi": "Navsari", "min": 6400, "modal": 6850, "max": 7100},
        {"date": "2024-06-09", "mandi": "Navsari", "min": 6300, "modal": 6700, "max": 6900},
        {"date": "2024-06-08", "mandi": "Navsari", "min": 6200, "modal": 6580, "max": 6750},
        {"date": "2024-06-07", "mandi": "Surat",   "min": 6150, "modal": 6500, "max": 6800},
        {"date": "2024-06-06", "mandi": "Surat",   "min": 6000, "modal": 6400, "max": 6600},
        {"date": "2024-06-05", "mandi": "Bharuch",  "min": 5900, "modal": 6300, "max": 6550},
        {"date": "2024-06-04", "mandi": "Bharuch",  "min": 5800, "modal": 6200, "max": 6450},
    ],
    "groundnut": [
        {"date": "2024-06-10", "mandi": "Junagadh", "min": 4800, "modal": 5100, "max": 5400},
        {"date": "2024-06-09", "mandi": "Junagadh", "min": 4750, "modal": 5050, "max": 5350},
        {"date": "2024-06-08", "mandi": "Rajkot",   "min": 4700, "modal": 4980, "max": 5200},
        {"date": "2024-06-07", "mandi": "Rajkot",   "min": 4650, "modal": 4950, "max": 5150},
    ],
    "wheat": [
        {"date": "2024-06-10", "mandi": "Ahmedabad", "min": 2100, "modal": 2250, "max": 2400},
        {"date": "2024-06-09", "mandi": "Ahmedabad", "min": 2080, "modal": 2230, "max": 2380},
        {"date": "2024-06-08", "mandi": "Vadodara",  "min": 2050, "modal": 2200, "max": 2350},
    ],
}


async def _fetch_agmarknet(crop: str, state: str = "Gujarat") -> Optional[list[dict]]:
    """Fetch live prices from Agmarknet/data.gov.in if API key is available."""
    if not settings.AGMARKNET_API_KEY:
        return None
    try:
        import httpx
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": settings.AGMARKNET_API_KEY,
            "format": "json",
            "filters[Commodity]": crop.title(),
            "filters[State]": state,
            "limit": 30,
            "sort[Arrival_Date]": "desc",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("records", [])
    except Exception as e:
        logger.warning("Agmarknet fetch failed", error=str(e))
        return None


def _calculate_trend(prices: list[dict]) -> dict:
    """Simple linear trend over modal prices."""
    if len(prices) < 2:
        return {"direction": "stable", "pct_change": 0, "forecast_7d": prices[0]["modal"] if prices else 0}
    modals = [p["modal"] for p in prices]
    first, last = modals[-1], modals[0]  # prices are newest-first
    pct = ((last - first) / first * 100) if first else 0
    direction = "rising" if pct > 2 else "falling" if pct < -2 else "stable"
    # Simple extrapolation
    forecast = round(last + (last - first) * 0.5, 0)
    return {"direction": direction, "pct_change": round(pct, 1), "forecast_7d": forecast}


async def run_market_insights_agent(
    crop: str = "cotton",
    district: str = "Surat",
    language: str = "en",
) -> AgentOutput:
    start = time.time()
    granite = get_granite_client()
    is_live = False

    # Try live data
    live_data = None
    if not settings.USE_MOCK_LLM and settings.AGMARKNET_API_KEY:
        live_data = await _fetch_agmarknet(crop)
        if live_data:
            is_live = True
            prices = [{"date": r.get("Arrival_Date"), "mandi": r.get("Market"), "min": float(r.get("Min_x0020_Price", 0)), "modal": float(r.get("Modal_x0020_Price", 0)), "max": float(r.get("Max_x0020_Price", 0))} for r in live_data[:7]]
        else:
            prices = SAMPLE_PRICES.get(crop.lower(), SAMPLE_PRICES["cotton"])
    else:
        prices = SAMPLE_PRICES.get(crop.lower(), SAMPLE_PRICES["cotton"])

    trend = _calculate_trend(prices)
    latest = prices[0] if prices else {}

    prompt = f"""You are KisanSathi's market analyst. Help a farmer decide when to sell their crop.

Crop: {crop} | District: {district}
Latest price at {latest.get('mandi', 'local mandi')}: Min ₹{latest.get('min',0)}/q, Modal ₹{latest.get('modal',0)}/q, Max ₹{latest.get('max',0)}/q
7-day trend: {trend['direction']} ({trend['pct_change']:+.1f}%)
7-day price forecast: ~₹{trend['forecast_7d']}/quintal
Data source: {'Live Agmarknet' if is_live else 'Sample CSV (not live data)'}

Provide:
1. Current market situation in 2 sentences
2. Best time to sell advice (hold/sell now/sell in X days)
3. 2 cost-saving tips for storage/transport
4. Nearest mandis to consider

Max 200 words. Respond in {language}. Be honest if data is sample/not live."""

    result = await granite.generate(prompt, mock_key="market_insights", max_tokens=350, temperature=0.3)

    source = Source(
        title="Agmarknet — Live Mandi Prices" if is_live else "Sample Market Data CSV (not live)",
        url="https://agmarknet.gov.in" if is_live else None,
        is_sample=not is_live,
    )

    return AgentOutput(
        agent_name="market_insights",
        answer=result["text"],
        confidence=0.85 if is_live else 0.6,
        sources=[source],
        tool_calls=["agmarknet_api" if is_live else "sample_csv", "trend_calculation"],
        latency_ms=(time.time() - start) * 1000,
        is_mock=result["is_mock"],
        extra={"prices": prices[:5], "trend": trend, "is_live_data": is_live},
    )
