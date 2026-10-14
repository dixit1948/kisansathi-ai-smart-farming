"""
Weather & Irrigation Agent — Open-Meteo forecast + ET0-based irrigation recommendation.
"""
import time
from typing import Optional
import httpx
import structlog
from app.agents.schemas import AgentOutput, Source
from app.core.config import settings
from app.core.granite import get_granite_client

logger = structlog.get_logger(__name__)

MOCK_WEATHER_DATA = {
    "location": "Surat, Gujarat",
    "forecast": [
        {"date": "2024-06-10", "max_temp": 38, "min_temp": 26, "rain_mm": 0, "wind_kmh": 12, "humidity_pct": 65},
        {"date": "2024-06-11", "max_temp": 37, "min_temp": 25, "rain_mm": 2, "wind_kmh": 18, "humidity_pct": 70},
        {"date": "2024-06-12", "max_temp": 36, "min_temp": 24, "rain_mm": 15, "wind_kmh": 8, "humidity_pct": 80},
        {"date": "2024-06-13", "max_temp": 34, "min_temp": 23, "rain_mm": 20, "wind_kmh": 6, "humidity_pct": 85},
        {"date": "2024-06-14", "max_temp": 35, "min_temp": 24, "rain_mm": 5, "wind_kmh": 10, "humidity_pct": 75},
        {"date": "2024-06-15", "max_temp": 38, "min_temp": 26, "rain_mm": 0, "wind_kmh": 14, "humidity_pct": 68},
        {"date": "2024-06-16", "max_temp": 39, "min_temp": 27, "rain_mm": 0, "wind_kmh": 16, "humidity_pct": 62},
    ],
    "irrigation_needed_mm": 40,
    "spray_window": "Best window: June 10 morning (low wind). Avoid June 11 (wind >15 km/h).",
    "alerts": ["Heat stress warning: max temp >38°C on June 10, 15, 16 — ensure adequate soil moisture"],
}


async def _fetch_open_meteo(lat: float, lon: float) -> Optional[dict]:
    """Fetch 7-day forecast from Open-Meteo free API."""
    try:
        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean",
            "timezone": "Asia/Kolkata",
            "forecast_days": 7,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning("Open-Meteo fetch failed", error=str(e))
        return None


def _calculate_et0(max_temp: float, min_temp: float, humidity: float) -> float:
    """Simplified Hargreaves ET0 estimate (mm/day)."""
    mean_temp = (max_temp + min_temp) / 2
    td = max_temp - min_temp
    # Hargreaves-Samani simplified
    return max(0.0023 * (mean_temp + 17.8) * (td ** 0.5) * 0.0135 * (mean_temp + 17.8), 0)


async def run_weather_irrigation_agent(
    lat: float = 21.17,
    lon: float = 72.83,
    soil_type: str = "loam",
    irrigation_type: str = "drip",
    crop: Optional[str] = None,
    language: str = "en",
) -> AgentOutput:
    start = time.time()
    granite = get_granite_client()

    if settings.USE_MOCK_LLM:
        weather_data = MOCK_WEATHER_DATA
    else:
        raw = await _fetch_open_meteo(lat, lon)
        if raw:
            weather_data = _parse_open_meteo(raw)
        else:
            weather_data = MOCK_WEATHER_DATA

    # Build prompt
    prompt = f"""You are KisanSathi's weather and irrigation advisor.
Based on the 7-day forecast below, provide:
1. Key weather risks (heat, rain, wind) for this week
2. Irrigation recommendation (amount in mm, timing)
3. Pesticide spray window (best days with low wind)
4. Any urgent action needed

Forecast data: {weather_data}
Soil type: {soil_type}
Irrigation system: {irrigation_type}
Crop: {crop or 'general'}
Language: {language}

Be specific. Give amounts and days. Max 250 words. Respond in {language}."""

    result = await granite.generate(prompt, mock_key="weather_irrigation", max_tokens=400, temperature=0.2)

    return AgentOutput(
        agent_name="weather_irrigation",
        answer=result["text"],
        confidence=0.9,
        sources=[Source(title="Open-Meteo 7-day forecast", url="https://api.open-meteo.com", is_sample=settings.USE_MOCK_LLM)],
        tool_calls=["open_meteo_api", "et0_calculation"],
        latency_ms=(time.time() - start) * 1000,
        is_mock=result["is_mock"],
        extra={"raw_forecast": weather_data.get("forecast", [])[:3]},
    )


def _parse_open_meteo(raw: dict) -> dict:
    """Parse Open-Meteo API response into our internal format."""
    daily = raw.get("daily", {})
    dates = daily.get("time", [])
    forecast = []
    for i, date in enumerate(dates):
        max_t = (daily.get("temperature_2m_max") or [None])[i]
        min_t = (daily.get("temperature_2m_min") or [None])[i]
        rain = (daily.get("precipitation_sum") or [0])[i] or 0
        wind = (daily.get("windspeed_10m_max") or [0])[i] or 0
        hum = (daily.get("relative_humidity_2m_mean") or [60])[i] or 60
        forecast.append({"date": date, "max_temp": max_t, "min_temp": min_t, "rain_mm": rain, "wind_kmh": wind, "humidity_pct": hum})
    total_rain = sum(f["rain_mm"] for f in forecast)
    et0_total = sum(_calculate_et0(f["max_temp"] or 30, f["min_temp"] or 20, f["humidity_pct"] or 65) for f in forecast)
    return {
        "forecast": forecast,
        "irrigation_needed_mm": max(0, round(et0_total - total_rain, 1)),
        "spray_window": next((f["date"] for f in forecast if f["wind_kmh"] < 15 and f["rain_mm"] == 0), "Check tomorrow"),
        "alerts": [f"High wind on {f['date']}" for f in forecast if f["wind_kmh"] > 20],
    }
