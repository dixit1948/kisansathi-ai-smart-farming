"""Agents package."""
from app.agents.supervisor import run_supervisor
from app.agents.crop_advisory import run_crop_advisory_agent
from app.agents.weather_irrigation import run_weather_irrigation_agent
from app.agents.pest_disease import run_pest_disease_agent
from app.agents.market_insights import run_market_insights_agent

__all__ = [
    "run_supervisor",
    "run_crop_advisory_agent",
    "run_weather_irrigation_agent",
    "run_pest_disease_agent",
    "run_market_insights_agent",
]
