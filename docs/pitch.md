# KisanSathi — Product Pitch & Innovation Deck

## 1. Problem Statement
Agriculture accounts for 18% of India's GDP and employs over 150 million citizens. Yet, Indian smallholders suffer from an average **30-40% yield loss** due to:
1. **Unpredictable Micro-Climates:** Erratic monsoons, heat stress, and improper irrigation cycles deplete soil and waste water.
2. **Pest & Disease Outbreaks:** Unchecked outbreaks (like Pink Bollworm in cotton) wipe out entire crops within 7-10 days.
3. **Fragmented & Delayed Advisory:** The farmer-to-extension-officer ratio in India is **1:1,162**. Expert visits happen weeks after symptoms appear.
4. **Information Asymmetry:** Farmers sell to intermediaries at distress rates due to lack of local Mandi price intelligence.
5. **Language & Digital Divide:** Generic advisories published in bureaucratic English fail to reach farmers who communicate primarily via regional dialects and voice messages.

---

## 2. Solution: KisanSathi
**KisanSathi** is an AI-powered Multi-Agent Smart Farming Advisor built on **IBM Granite Foundation Models via watsonx.ai**. It delivers hyper-personalized, real-time agronomic guidance directly through **WhatsApp** (farmers' primary app) and a high-performance **Offline-capable PWA**.

### Core Value Pillars
- **<10s Diagnosis:** Instant leaf disease diagnosis from a phone photo with organic-first remediation and strict chemical caution.
- **Weather-Aware Irrigation:** 7-day Open-Meteo forecasts combined with Penman-Monteith ET0 calculations to prevent water waste.
- **Mandi Price Intelligence:** Live APMC mandi price tracking and quantitative sell-timing recommendations.
- **Vernacular First:** Gujarati, Hindi, and English auto-detection with plain Grade-6 conversational copy.
- **Extension Officer Force Multiplier:** Geospatial epidemiology heatmap clustering outbreaks so officers can dispatch targeted taluka advisories before pests spread.

---

## 3. Technical Innovation & IBM Granite Advantage
- **LangGraph Multi-Agent Architecture:** Rather than a monolithic LLM, KisanSathi employs a Supervisor agent orchestrating 4 specialized domain agents (Crop Advisory, Weather & Irrigation, Pest & Disease, Market Insights). Independent sub-tasks run in parallel.
- **IBM Granite 13B & Vision on watsonx.ai:** Domain-adapted reasoning models providing high grounding and minimal hallucination.
- **Granite Guardian & Safety Guardrails:** Strict prompt injection defenses, non-farming refusal filters, and prevention of hallucinated chemical dosages.
- **Hybrid RAG Engine:** Combining ChromaDB dense embeddings with BM25 keyword matching across certified ICAR, KVK, and PlantVillage corpus documents.
- **Zero-Downtime Deterministic Fallback (`USE_MOCK_LLM=true`):** Guarantees 100% demo uptime and resilience even in offline or disconnected field environments.

---

## 4. Impact & Scalability
- **Farmer Income Increase:** Estimated 15-20% margin uplift through timely mandi timing and reduced chemical over-application.
- **Water Conservation:** ET0-based drip irrigation scheduling saves up to 35% irrigation water in water-stressed districts.
- **DPDP Act 2023 Compliant:** Complete consent recording, data minimization, and right-to-erasure workflows built in from Day 1.

---

## 5. Strategic Roadmap
- **Phase 1 (Current):** Multimodal disease scan, LangGraph supervisor, WhatsApp bot, PWA web dashboard, Surat/Navsari/Bharuch pilot data.
- **Phase 2 (Next 6 Months):** Drone imagery ingestion for field-level NDVI mapping; local Whisper audio pipeline for dialect voice notes.
- **Phase 3 (Next 12 Months):** Integration with ONDC Agri-Bazaar for direct farm-to-buyer sales without middlemen.
