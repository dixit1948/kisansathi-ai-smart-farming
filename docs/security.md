# KisanSathi — Security Architecture & OWASP Mapping

## 1. OWASP Top 10 (Web Applications) Mapping

| Threat | Description | KisanSathi Mitigation | Implementation File |
|---|---|---|---|
| **A01: Broken Access Control** | Unauthorized access to other users' farms, scans, or chats | Role-Based Access Control (`FARMER`, `OFFICER`, `ADMIN`) + Object-Level Ownership checks (`verify_farmer_ownership`). Farmers cannot query another farmer's UUID. | `backend/app/api/deps.py`, `backend/app/api/v1/routers/farms.py` |
| **A02: Cryptographic Failures** | Compromised passwords or token leaks | Argon2 password hashing with per-user salt; JWT access tokens (15m expiry) + rotating HttpOnly refresh tokens; TLS encryption. | `backend/app/core/security.py` |
| **A03: Injection** | SQL, NoSQL, or Command Injection | SQLAlchemy 2 async ORM with parameterized queries exclusively. Zero raw SQL string concatenation. Pydantic v2 input parsing. | `backend/app/core/database.py`, `backend/app/api/` |
| **A04: Insecure Design** | Rate abuse, lack of business-logic limits | Sliding window rate limiting per IP and per user; max upload size limits (10MB); OTP generation throttled to 5 per hour. | `backend/app/core/security_middleware.py`, `backend/app/api/v1/routers/auth.py` |
| **A05: Security Misconfiguration** | Missing security headers, exposed stack traces | Automated SecurityHeadersMiddleware adding HSTS, CSP, X-Frame-Options (DENY), X-Content-Type-Options (nosniff), Referrer-Policy. Generic 500 error envelopes without internal stack trace leaks. | `backend/app/core/security_middleware.py`, `backend/app/main.py` |
| **A06: Vulnerable & Outdated Components** | Known CVEs in dependencies | Pinned dependencies in `requirements.txt`; regular `pip-audit` and `bandit` scans in CI workflow. | `backend/requirements.txt`, `.github/workflows/ci.yml` |
| **A07: Identification & Auth Failures** | Brute force OTP or token reuse | Constant-time password comparison, rotating refresh tokens, rate-limited login endpoints. | `backend/app/core/security.py`, `backend/app/api/v1/routers/auth.py` |
| **A08: Software & Data Integrity Failures** | WhatsApp webhook spoofing | Webhook validation enforces Meta `X-Hub-Signature-256` HMAC-SHA256 verification using secret key. Nonce/timestamp replay protection. | `backend/app/api/v1/routers/webhook.py` |
| **A09: Security Logging & Monitoring** | Undetected intrusion or misuse | Structured JSON logging with unique `request_id`, audit logging of all officer/admin actions, Prometheus metric counters. | `backend/app/core/logging.py`, `backend/app/models/trace.py` |
| **A10: Server-Side Request Forgery (SSRF)** | Exploitation of weather/market fetch APIs | Outbound requests strictly allow-listed to known Open-Meteo & Agmarknet hostnames. No user-supplied URLs executed by backend. | `backend/app/agents/weather_irrigation.py` |

---

## 2. OWASP Top 10 for LLM Applications Mapping

| Threat | Description | KisanSathi Mitigation | Implementation File |
|---|---|---|---|
| **LLM01: Prompt Injection** | Attacker injects malicious instructions inside query or image | Strict boundary separation: User query isolated in separate system/context templates. Retrieved RAG text explicitly framed as untrusted contextual reference. | `backend/app/core/granite.py`, `backend/app/agents/crop_advisory.py` |
| **LLM02: Insecure Output Handling** | LLM outputs malicious scripts or raw HTML | Strict JSON / Pydantic schema validation on all agent outputs. All UI rendering uses text nodes or sanitized Markdown. | `backend/app/agents/schemas.py`, `frontend/src/` |
| **LLM03: Training Data Poisoning** | Malicious RAG documents | Curated knowledge base strictly loaded from verified agricultural sources (ICAR, KVK, PlantVillage) with source hash validation. | `backend/scripts/ingest.py` |
| **LLM04: Model Denial of Service** | Resource exhaustion via huge prompts | Token and character limits enforced on user queries (max 1000 chars); timeout limits (15s) on all agent invocations. | `backend/app/agents/supervisor.py` |
| **LLM05: Supply Chain Vulnerabilities** | Rogue weights or libraries | Official `ibm-watsonx-ai` SDK with verified model identifiers (`ibm/granite-13b-instruct-v2`). | `backend/app/core/granite.py` |
| **LLM06: Sensitive Information Disclosure** | PII leakage in LLM output | PII minimisation: Farmer personal phone/address is stripped from prompts sent to LLM; only agro-climatic context (soil, crop, district) is passed. | `backend/app/agents/supervisor.py` |
| **LLM07: Insecure Plugin / Tool Design** | Agents calling arbitrary tools | Strict static tool allow-listing; agents only call pre-approved deterministic python functions with typed inputs. | `backend/app/agents/` |
| **LLM08: Excessive Agency** | Agent autonomously taking real-world actions | Advisory-only guardrail: AI never initiates financial transactions or automated sprayers; explicit disclaimers provided. | `backend/app/agents/schemas.py` |
| **LLM09: Overreliance / Hallucination** | Incorrect pesticide dosage hallucinated | Strict Grounding Rule: Pest & Disease Agent must refuse to output chemical dosages not explicitly present in retrieved ICAR sources. Organic remedies prioritized. | `backend/app/agents/pest_disease.py` |
| **LLM10: Model Theft** | Extraction of proprietary prompts | API endpoints authenticated behind JWT with rate limits; prompts kept server-side. | `backend/app/core/security.py` |

---

## 3. Data Protection (DPDP Act 2023 Alignment)
- **Consent Architecture:** Timestamped consent captured during registration (`consent_given_at`).
- **Data Export:** Farmer can download all their data (profile, scans, chat history) via `GET /api/v1/farmers/me/export`.
- **Right to Erasure (Delete Account):** Soft-delete and hard-anonymization workflow via `DELETE /api/v1/farmers/me`.
- **Image Sanitization:** Uploaded leaf images have EXIF GPS metadata stripped using Pillow before filesystem storage.
