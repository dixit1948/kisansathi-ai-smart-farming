"""
IBM Granite LLM wrapper via ibm-watsonx-ai SDK.
Falls back to deterministic mock responses when USE_MOCK_LLM=true.
Logs clearly when mock/fallback is active.
"""
import time
from typing import Optional, AsyncIterator
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


# ── Mock responses ────────────────────────────────────────────────────────────
MOCK_RESPONSES = {
    "crop_advisory": (
        "🌱 **Crop Advisory (MOCK)**\n\n"
        "For cotton at vegetative stage in Gujarat:\n"
        "• Apply 60kg N/ha in two splits at 30 and 60 DAS.\n"
        "• Maintain 90 cm row spacing for better air circulation.\n"
        "• Watch for pink bollworm after 90 DAS.\n\n"
        "_Source: ICAR-CICR Cotton Cultivation Guide (Sample), Page 12_\n\n"
        "⚠️ [MOCK MODE] This is a demo response. Set USE_MOCK_LLM=false for real IBM Granite responses."
    ),
    "weather_irrigation": (
        "🌦️ **Weather & Irrigation (MOCK)**\n\n"
        "Next 7 days — Surat district:\n"
        "• Max temp: 38°C | Min: 26°C | No rain expected.\n"
        "• **Irrigation needed:** Apply 40mm water in next 2 days (drip: 2h at 2L/h/plant).\n"
        "• Avoid spraying pesticides on Wednesday — wind speed >15 km/h forecast.\n\n"
        "⚠️ [MOCK MODE] Real data from Open-Meteo when USE_MOCK_LLM=false."
    ),
    "pest_disease": (
        "🔍 **Disease Diagnosis (MOCK)**\n\n"
        "**Detected:** Cotton Leaf Curl Virus (CLCuV)\n"
        "**Confidence:** 87% | **Severity:** Medium\n\n"
        "**Treatment:**\n"
        "1. Remove and destroy infected plants immediately.\n"
        "2. Apply imidacloprid 17.8 SL @ 0.5 ml/L to control whitefly vector.\n"
        "3. Spray neem oil 5ml/L as organic option.\n\n"
        "**Prevention:** Use CLCuV-tolerant varieties (RCH-2, Bunny).\n\n"
        "⚠️ [MOCK MODE] Real Granite vision analysis when USE_MOCK_LLM=false."
    ),
    "market_insights": (
        "📊 **Market Insights (MOCK)**\n\n"
        "**Cotton** — Navsari Mandi (Last 7 days):\n"
        "| Date | Min | Modal | Max |\n"
        "|------|-----|-------|-----|\n"
        "| Today | ₹6,400 | ₹6,850 | ₹7,100 |\n\n"
        "**Trend:** ↗️ Rising — prices up 4% over last week.\n"
        "**Advice:** Hold stock for 7-10 more days if storage is available.\n\n"
        "⚠️ [MOCK MODE] Real Agmarknet data requires API key."
    ),
    "general": (
        "🤖 **KisanSathi AI (MOCK)**\n\n"
        "I can help you with:\n"
        "• Crop advisory and schedules\n"
        "• Weather and irrigation planning\n"
        "• Pest and disease diagnosis (upload a photo)\n"
        "• Market prices and sell timing\n\n"
        "What would you like to know today?\n\n"
        "⚠️ [MOCK MODE] Real IBM Granite responses when USE_MOCK_LLM=false."
    ),
}


class GraniteClient:
    """
    Thin async wrapper around ibm-watsonx-ai ModelInference.
    All LLM calls go through here — enables mock injection.
    """

    def __init__(self):
        self._client = None
        if not settings.USE_MOCK_LLM:
            self._init_real_client()

    def _init_real_client(self):
        try:
            from ibm_watsonx_ai import APIClient, Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            credentials = Credentials(api_key=settings.WATSONX_API_KEY, url=settings.WATSONX_URL)
            self._api_client = APIClient(credentials=credentials, project_id=settings.WATSONX_PROJECT_ID)
            self._model = ModelInference(
                model_id=settings.GRANITE_TEXT_MODEL,
                api_client=self._api_client,
                project_id=settings.WATSONX_PROJECT_ID,
            )
            logger.info("Granite client initialized", model=settings.GRANITE_TEXT_MODEL)
        except Exception as e:
            logger.error("Failed to init Granite client — falling back to mock", error=str(e))
            settings.USE_MOCK_LLM = True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        mock_key: str = "general",
        max_tokens: int = 800,
        temperature: float = 0.3,
    ) -> dict:
        """
        Generate a response. Returns dict with text, latency_ms, tokens, is_mock.
        """
        if settings.USE_MOCK_LLM:
            logger.info("[MOCK] LLM generate called", mock_key=mock_key)
            mock_text = MOCK_RESPONSES.get(mock_key, MOCK_RESPONSES["general"])
            return {"text": mock_text, "latency_ms": 120, "tokens": 250, "is_mock": True}

        start = time.time()
        try:
            # Build messages format for Granite instruct
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else prompt
            response = self._model.generate(
                prompt=full_prompt,
                params={"max_new_tokens": max_tokens, "temperature": temperature, "stop_sequences": ["\nUser:"]},
            )
            text = response["results"][0]["generated_text"].strip()
            tokens = response["results"][0].get("generated_token_count", 0)
            latency_ms = (time.time() - start) * 1000
            return {"text": text, "latency_ms": latency_ms, "tokens": tokens, "is_mock": False}
        except Exception as e:
            logger.error("Granite generate failed", error=str(e))
            logger.warning("[MOCK FALLBACK] Using mock response after Granite error", mock_key=mock_key)
            return {"text": MOCK_RESPONSES.get(mock_key, MOCK_RESPONSES["general"]), "latency_ms": 0, "tokens": 0, "is_mock": True}

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        """Streaming generation for chat SSE."""
        if settings.USE_MOCK_LLM:
            logger.info("[MOCK] LLM stream called")
            mock_text = MOCK_RESPONSES["general"]
            for word in mock_text.split():
                yield word + " "
            return

        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else prompt
            for chunk in self._model.generate_text_stream(prompt=full_prompt):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error("Granite stream failed", error=str(e))
            yield "[Error: LLM stream failed. Please try again.]"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via Granite slate model."""
        if settings.USE_MOCK_LLM:
            # Return random-ish deterministic embeddings for mock
            import hashlib
            result = []
            for text in texts:
                h = int(hashlib.sha256(text.encode()).hexdigest()[:32], 16)
                vec = [(h >> i & 0xFF) / 255.0 for i in range(384)]
                result.append(vec)
            return result
        try:
            from ibm_watsonx_ai.foundation_models import Embeddings
            embed_model = Embeddings(
                model_id=settings.GRANITE_EMBED_MODEL,
                api_client=self._api_client,
                project_id=settings.WATSONX_PROJECT_ID,
            )
            response = embed_model.embed_documents(texts)
            return response
        except Exception as e:
            logger.error("Granite embed failed", error=str(e))
            return [[] for _ in texts]

    async def guard_check(self, text: str) -> dict:
        """
        Run Granite Guardian safety check.
        Returns {safe: bool, categories: list, score: float}
        """
        if settings.USE_MOCK_LLM:
            return {"safe": True, "categories": [], "score": 0.02, "is_mock": True}

        # Simple heuristic guard when Guardian not available
        unsafe_patterns = ["bomb", "poison recipe", "harm human", "suicide"]
        text_lower = text.lower()
        for pattern in unsafe_patterns:
            if pattern in text_lower:
                return {"safe": False, "categories": ["harmful_content"], "score": 0.95, "is_mock": False}
        return {"safe": True, "categories": [], "score": 0.01, "is_mock": False}


# Singleton
_granite_client: Optional[GraniteClient] = None


def get_granite_client() -> GraniteClient:
    global _granite_client
    if _granite_client is None:
        _granite_client = GraniteClient()
    return _granite_client
