"""
Pydantic schemas shared by all agents — typed agent output.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


class Source(BaseModel):
    title: str
    section: Optional[str] = None
    page: Optional[str] = None
    url: Optional[str] = None
    is_sample: bool = False


class AgentOutput(BaseModel):
    """Standard typed output returned by every agent."""
    agent_name: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    sources: list[Source] = []
    tool_calls: list[str] = []
    latency_ms: float = 0.0
    is_mock: bool = False
    extra: Optional[dict[str, Any]] = None


class SupervisorOutput(BaseModel):
    """Final merged output from supervisor."""
    answer: str
    intent: str
    language: str = "en"
    agents_used: list[str] = []
    all_sources: list[Source] = []
    total_latency_ms: float = 0.0
    is_mock: bool = False
    trace_id: Optional[str] = None
    agent_outputs: list[AgentOutput] = []
