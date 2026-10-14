# 🌾 KisanSathi — AI Multi-Agent Smart Farming Advisor

> Personalised, real-time, sustainable farming advice powered by IBM Granite via watsonx.ai — delivered over WhatsApp and a progressive web app.

[![CI](https://github.com/your-org/kisansathi/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/kisansathi/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Variables](#environment-variables)
3. [Mock Mode (Demo)](#mock-mode-demo)
4. [WhatsApp Webhook Setup](#whatsapp-webhook-setup)
5. [IBM Cloud Deploy](#ibm-cloud-deploy)
6. [Architecture](#architecture)
7. [Troubleshooting](#troubleshooting)
8. [Manual Steps Required](#manual-steps-required)

---

## Quick Start

### Prerequisites

- Docker + Docker Compose ≥ v2.20
- Node.js 20+ (for frontend dev)
- Python 3.11+ (for backend dev)
- `make`

### 1. Clone & configure

```bash
git clone https://github.com/your-org/kisansathi.git
cd kisansathi
cp backend/.env.example backend/.env
# Edit backend/.env — set at minimum WATSONX_API_KEY and WATSONX_PROJECT_ID
# Or set USE_MOCK_LLM=true to run fully offline
```

### 2. Run with Docker Compose (recommended)

```bash
make docker-up
# Services start: api :8000, web :3000, postgres :5432, redis :6379, chroma :8001
# Seed data is loaded automatically on first run
```

Open [http://localhost:3000](http://localhost:3000)

Demo login (seeded):
| Role    | Phone/Email         | Password    |
|---------|---------------------|-------------|
| Farmer  | +91 98765 43210     | Demo@1234   |
| Officer | officer@kvk.gov.in  | Demo@1234   |
| Admin   | admin@kisansathi.in | Admin@1234  |

### 3. Run in dev mode (hot-reload)

```bash
make dev          # starts backend + frontend with hot reload
make seed         # re-seed DB (idempotent)
make test         # run all tests
make lint         # lint + type-check
```

---

## Environment Variables

See [`backend/.env.example`](backend/.env.example) for the full list. Critical ones:

| Variable | Description | Default |
|---|---|---|
| `WATSONX_API_KEY` | IBM Cloud API key | — |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | — |
| `WATSONX_URL` | watsonx.ai endpoint | `https://us-south.ml.cloud.ibm.com` |
| `USE_MOCK_LLM` | `true` = deterministic mock, no API calls | `false` |
| `DATABASE_URL` | PostgreSQL DSN | postgres://... |
| `SQLITE_FALLBACK` | `true` = use SQLite for dev | `false` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing key (32+ chars) | — |
| `WHATSAPP_VERIFY_TOKEN` | Meta webhook verify token | — |
| `WHATSAPP_APP_SECRET` | Meta app secret for HMAC | — |
| `WHATSAPP_ACCESS_TOKEN` | Meta permanent/system-user token | — |

---

## Mock Mode (Demo)

Set `USE_MOCK_LLM=true` in `.env`. All LLM calls return deterministic, realistic mock responses. The console logs `[MOCK]` prefixes clearly. The demo never breaks without an API key.

---

## WhatsApp Webhook Setup

1. Create a Meta App at [developers.facebook.com](https://developers.facebook.com).
2. Add WhatsApp product → get a test number.
3. Webhook URL: `https://<your-domain>/api/v1/webhook/whatsapp`
4. Verify token: same as `WHATSAPP_VERIFY_TOKEN` in `.env`.
5. Subscribe to `messages` field.
6. For local dev, use [ngrok](https://ngrok.com): `ngrok http 8000` → use the HTTPS URL.
7. Set `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_APP_SECRET` from the Meta dashboard.

---

## IBM Cloud Deploy

```bash
# 1. Login
ibmcloud login --sso
ibmcloud target -r us-south -g default

# 2. Create Code Engine project
ibmcloud ce project create --name kisansathi

# 3. Create secrets
ibmcloud ce secret create --name kisansathi-secrets \
  --from-literal WATSONX_API_KEY=<your-key> \
  --from-literal SECRET_KEY=<your-jwt-secret> \
  --from-literal WHATSAPP_APP_SECRET=<your-secret>

# 4. Deploy API
ibmcloud ce application create \
  --name kisansathi-api \
  --image icr.io/your-namespace/kisansathi-api:latest \
  --env-from-secret kisansathi-secrets \
  --port 8000 \
  --min-scale 1

# 5. Deploy Web
ibmcloud ce application create \
  --name kisansathi-web \
  --image icr.io/your-namespace/kisansathi-web:latest \
  --port 3000

# See infra/ibm-cloud-deploy.md for full guide with IBM Cloud Databases for PostgreSQL
```

---

## Architecture

```
Farmer (WhatsApp / PWA)
        │
        ▼
Meta Cloud API ──► FastAPI Backend (/api/v1)
                        │
              ┌─────────┼──────────┐
              ▼         ▼          ▼
         LangGraph   ChromaDB    PostgreSQL
         Supervisor   (RAG)       (State)
              │
    ┌─────────┼──────────┬────────────┐
    ▼         ▼          ▼            ▼
  Crop     Weather   Pest/Disease  Market
 Advisory   Agent      Agent       Agent
  Agent       │          │           │
    └─────────┴──────────┴───────────┘
                        │
              IBM Granite (watsonx.ai)
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `WATSONX_API_KEY not set` | Set in `.env` or use `USE_MOCK_LLM=true` |
| DB connection refused | Run `docker-compose up postgres` first |
| ChromaDB not ready | Wait 10s after `docker-compose up`, chroma takes time |
| WhatsApp 403 | Check `WHATSAPP_APP_SECRET` and HMAC verification |
| Frontend blank | Check `VITE_API_URL` in `frontend/.env` |

---

## Manual Steps Required

After cloning, you **must** do these manually:

1. **watsonx.ai:** Create IBM Cloud account → provision watsonx.ai → get API key + project ID → set in `.env`
2. **WhatsApp:** Create Meta Developer App → get phone number token + app secret → set in `.env`
3. **IBM Cloud (production):** `ibmcloud login` → follow deploy guide above
4. **JWT Secret:** Generate with `python -c "import secrets; print(secrets.token_hex(32))"` → set `SECRET_KEY`
5. **Knowledge base:** Add your own PDFs to `knowledge/` → run `make ingest`

> ⚠️ **Honest disclosure:** LLM responses use IBM Granite via watsonx.ai SDK. In `USE_MOCK_LLM=true` mode, responses are hardcoded samples. Market prices are sample CSV data — not live Agmarknet (API key required). Weather uses Open-Meteo free API (no key needed). Leaf disease uses a mock ONNX classifier in mock mode.

---

## Screenshots

> _Run the app and add screenshots here_

| Landing | Dashboard | Disease Scan | Chat |
|---------|-----------|--------------|------|
| ![landing](docs/screenshots/landing.png) | ![dashboard](docs/screenshots/dashboard.png) | ![scan](docs/screenshots/scan.png) | ![chat](docs/screenshots/chat.png) |
