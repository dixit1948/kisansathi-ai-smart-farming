# KisanSathi — System Architecture

## 1. High-Level Architecture Diagram (Mermaid)

```mermaid
flowchart TB
    subgraph Channels ["User Access Channels"]
        WA["Meta WhatsApp Cloud API\n(Farmer / Field Worker)"]
        WEB["React 18 PWA\n(Desktop, Mobile Android/iOS)"]
    end

    subgraph Gateway ["Edge & Security Gateway"]
        CORS["CORS & CSRF Guard"]
        RATE["Token Bucket Rate Limiter"]
        SEC["Security Headers\n(CSP, HSTS, X-Frame)"]
        WH_VERIFY["HMAC-SHA256 Webhook Validator"]
    end

    subgraph API ["FastAPI 0.111 Application Core"]
        ROUTER["Versioned Routers (/api/v1)\nAuth, Farm, Chat, Scan, Weather, Market, Officer"]
        DEP["FastAPI Depends Injection\nRBAC & Object-Level Authz"]
        UPLOAD["Sanitizer & EXIF Stripper\nMagic Bytes Validation"]
    end

    subgraph Agents ["LangGraph Multi-Agent Supervisor Engine"]
        SUP["LangGraph Supervisor\nIntent Classification & Synthesis"]
        CROP_AG["Crop Advisory Agent\n(Hybrid RAG: Vector + BM25)"]
        WEATH_AG["Weather & Irrigation Agent\n(Open-Meteo ET0 & Spray Windows)"]
        PEST_AG["Pest & Disease Agent\n(Multimodal Leaf Diagnostics)"]
        MKT_AG["Market Insights Agent\n(Agmarknet / Mandi Trend Predictor)"]
    end

    subgraph Models ["IBM watsonx.ai Granite Foundation Models"]
        G_TXT["IBM Granite 13B Instruct\n(Text Reasoning & Multi-lingual Merging)"]
        G_VIS["IBM Granite Vision / PlantNet\n(Leaf Pathology Classification)"]
        G_EMB["IBM Slate / Multilingual Embeddings\n(Vector Similarity)"]
        G_GUARD["Granite Guardian / Input-Output Safety\n(Prompt Injection & Dosage Guard)"]
        MOCK_LLM["Deterministic Fallback Engine\n(USE_MOCK_LLM=true)"]
    end

    subgraph Storage ["Data & Vector Persistence"]
        PG[("PostgreSQL 16 / aiosqlite\nAsync SQLAlchemy 2 + Alembic")]
        CHROMA[("ChromaDB Vector Store\nICAR / KVK Farming Knowledge")]
        REDIS[("Redis 7 / Memory Cache\nToken Blacklist & Rate Limits")]
    end

    subgraph Background ["Background Automation"]
        SCHED["APScheduler Engine\nDaily 6am Digest & Outbreak Clusters"]
    end

    %% Wiring
    WA --> WH_VERIFY --> ROUTER
    WEB --> CORS --> RATE --> SEC --> ROUTER
    ROUTER --> DEP
    DEP --> UPLOAD
    ROUTER --> SUP
    SUP --> CROP_AG & WEATH_AG & PEST_AG & MKT_AG

    CROP_AG --> CHROMA
    CROP_AG & WEATH_AG & PEST_AG & MKT_AG --> G_TXT
    PEST_AG --> G_VIS
    CROP_AG --> G_EMB
    SUP --> G_GUARD
    G_TXT -.-> MOCK_LLM

    ROUTER --> PG
    ROUTER --> REDIS
    SCHED --> PG
```

## 2. Agent Interaction & Data Flow
1. **Request Intake:** A user message arrives via Web Chat or WhatsApp Webhook.
2. **Intent Classification:** Supervisor determines intent (`advisory`, `weather`, `disease_photo`, `market`, `general`).
3. **Parallel Dispatch:** If query spans multiple domains (e.g., "Can I irrigate and spray urea on my cotton tomorrow?"), Supervisor fans out to `crop_advisory` and `weather_irrigation` simultaneously via `asyncio.gather`.
4. **Safety & Guardrails:** Granite Guardian validates that no non-farming prompts, prompt injections, or unauthorized chemical dosages are processed.
5. **Synthesis:** Supervisor combines agent responses into a concise, actionable answer in Gujarati/Hindi/English with verified citations.
