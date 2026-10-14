# KisanSathi — UX Personas

## Persona 1: Primary User — Arjun Bhai Patel (Farmer)
- **Demographics:** 46 years old, smallholder farmer in Bardoli, Surat, Gujarat.
- **Context:** Cultivates 3.5 hectares of cotton and sugarcane. Speaks Gujarati natively, understands basic conversational Hindi. Uses a low-cost Android smartphone (₹8,000 range, 4G/2G intermittent connectivity).
- **Tech Literacy:** Low to moderate. Comfortable with WhatsApp voice notes and photo sharing; struggles with complex web portals, multi-level dropdowns, or English forms.
- **Pain Points:**
  - Pests (Pink bollworm) and leaf curls ruin yield before local agriculture officers can visit.
  - Sells produce at distress prices to local middlemen because mandi rates are opaque.
  - Water scarcity: relies on erratic canal cycles and over/under-irrigates black cotton soil.
- **Needs & Goals:**
  - Snap a photo of a sick leaf and get an immediate, trusted diagnosis in Gujarati.
  - Simple 1-tap WhatsApp voice or text chat with zero bureaucratic barrier.
  - Daily WhatsApp/PWA weather and irrigation reminder: "Water tomorrow for 2 hours, do not spray today due to wind."
  - Mandi price tracker with clear "Sell" or "Hold" recommendation.

---

## Persona 2: Ramesh Patel (Agri Extension Officer / KVK Scientist)
- **Demographics:** 38 years old, Krishi Vigyan Kendra (KVK) extension officer overseeing 120+ villages in Surat and Navsari districts.
- **Context:** Works on laptop and tablet; travels between taluka field visits and research labs. Speaks Gujarati, Hindi, and English fluently.
- **Tech Literacy:** High. Uses government MIS portals, GIS mapping, and spreadsheets.
- **Pain Points:**
  - Cannot physically visit 10,000+ farmers in his jurisdiction during sudden pest outbreaks.
  - Lacks real-time spatial visibility into emerging pest clusters (e.g., CLCuV spreading across Bardoli).
  - High manual workload answering repetitive queries regarding fertilizer schedules.
- **Needs & Goals:**
  - Geospatial dashboard showing real-time farmer alerts, heatmaps of pest diagnoses, and cluster alerts.
  - Ability to filter by crop (Cotton, Groundnut, Wheat) and taluka to dispatch targeted advisories.
  - Audit trail and verification of AI-recommended chemical dosages to ensure safety compliance.
  - Export CSV data for state agricultural department reports.

---

## Persona 3: System Administrator (KisanSathi Ops / Agri-Tech Co.)
- **Demographics:** DevSecOps & Platform Engineer managing cloud infra, LLM safety guardrails, and compliance.
- **Context:** Manages IBM Cloud deployment, watsonx.ai Granite instances, ChromaDB vectors, and Meta WhatsApp webhooks.
- **Tech Literacy:** Expert.
- **Needs & Goals:**
  - Real-time observability: agent latency, hallucination guards, rate limits, and fallback triggers.
  - DPDP Act 2023 compliance: user consent verification, audit logs, and data export/deletion workflows.
  - Zero-downtime reliability with mock fallback (`USE_MOCK_LLM=true`) during upstream API maintenance.
