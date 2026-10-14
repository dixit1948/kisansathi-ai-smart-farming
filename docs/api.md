# KisanSathi — API Reference Documentation

All endpoints are versioned under `/api/v1` and return structured JSON responses.

## Standard Error Envelope
```json
{
  "error": {
    "code": "VALIDATION_ERROR | NOT_FOUND | UNAUTHORIZED | FORBIDDEN | RATE_LIMITED | INTERNAL_ERROR",
    "message": "Human readable explanation",
    "details": {},
    "request_id": "b3f0e0f8-c292-491c-a077-d4f1349a37ad"
  }
}
```

---

## 1. Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/otp/send`
Request an OTP for mobile phone login.
- **Body:** `{ "phone": "+919876543210" }`
- **Response:** `200 OK` `{ "message": "OTP sent successfully", "expires_in_seconds": 600 }`

### `POST /api/v1/auth/otp/verify`
Verify phone OTP and obtain JWT tokens.
- **Body:** `{ "phone": "+919876543210", "otp": "123456" }`
- **Response:** `200 OK` `{ "access_token": "...", "token_type": "bearer", "role": "farmer", "user_id": "..." }`

### `POST /api/v1/auth/login`
Email and password login (for Officers and Admins).
- **Body:** `{ "email": "officer@kvk.gov.in", "password": "Demo@1234" }`
- **Response:** `200 OK` `{ "access_token": "...", "token_type": "bearer", "role": "officer" }`

---

## 2. Multi-Agent Chat (`/api/v1/chat`)

### `POST /api/v1/chat/message`
Main multi-agent chat endpoint invoking the LangGraph Supervisor.
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "message": "When should I apply first split nitrogen for cotton?",
  "language": "en",
  "crop": "cotton",
  "farm_id": "optional-uuid"
}
```
- **Response:** `200 OK`
```json
{
  "answer": "Apply 60kg N/ha in two splits at 30 and 60 DAS...",
  "intent": "advisory",
  "language": "en",
  "agents_used": ["crop_advisory", "weather_irrigation"],
  "all_sources": [
    {
      "title": "ICAR-CICR Cotton Cultivation Guide",
      "section": "Nutrient Management",
      "page": "12",
      "is_sample": true
    }
  ],
  "total_latency_ms": 142.5,
  "is_mock": true,
  "trace_id": "84a7e930-18e4-41d1-9689-53b92f763e02"
}
```

### `GET /api/v1/chat/stream`
Server-Sent Events (SSE) streaming endpoint for real-time word-by-word LLM replies.

---

## 3. Leaf Disease Scan (`/api/v1/scan`)

### `POST /api/v1/scan/upload`
Upload leaf image for multimodal disease classification.
- **Headers:** `Content-Type: multipart/form-data`
- **Form Data:**
  - `file`: image file (`.jpg`, `.png`, `.webp`, max 10MB)
  - `crop`: `"cotton"` (optional)
  - `farm_id`: UUID (optional)
- **Response:** `200 OK`
```json
{
  "id": "e9321f8a-...",
  "predicted_label": "Cotton Leaf Curl Virus (CLCuV)",
  "confidence": 0.87,
  "severity": "medium",
  "treatment_steps": [
    "Pull out and destroy infected plants immediately.",
    "Spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil @ 5ml/L."
  ],
  "chemical_options": [
    "Imidacloprid 17.8 SL @ 0.5 ml/L to control whitefly vector."
  ],
  "prevention_tips": [
    "Plant CLCuV-tolerant varieties (RCH-2, Bunny).",
    "Install yellow sticky traps (10/acre)."
  ],
  "sources": [{ "title": "ICAR-CICR Pathology", "is_sample": true }],
  "is_mock": true
}
```

### `GET /api/v1/scan/history`
Returns historical scans performed by the authenticated farmer.

---

## 4. Weather & Irrigation (`/api/v1/weather`)

### `GET /api/v1/weather/forecast?lat=21.17&lon=72.83&soil_type=black&irrigation_type=drip`
Retrieves 7-day agro-meteorological forecast with ET0 evapotranspiration water balance and pesticide spray window recommendations.

---

## 5. Market Insights (`/api/v1/market`)

### `GET /api/v1/market/prices?crop=cotton&mandi=Navsari&days=30`
Returns historical and forecast mandi prices, modal price trends, and a quantitative "Sell vs Hold" heuristic badge.

---

## 6. Extension Officer & Outbreak Clusters (`/api/v1/officer`)

### `GET /api/v1/officer/overview`
Aggregated stats: total farms monitored, active pest clusters, critical weather alerts.

### `GET /api/v1/officer/clusters`
Returns geospatial clusters of disease detections with latitude, longitude, radius, crop type, and farmer counts.

### `GET /api/v1/officer/export?format=csv`
Streams a CSV file containing all recent field incidents and diagnostic logs.

---

## 7. Meta WhatsApp Cloud API Webhook (`/api/v1/webhook/whatsapp`)

### `GET /api/v1/webhook/whatsapp`
Verification endpoint for Meta challenge: checks `hub.mode` and `hub.verify_token`.

### `POST /api/v1/webhook/whatsapp`
Inbound webhook receiving messages and photos. Validates `X-Hub-Signature-256` HMAC-SHA256 signature, parses sender phone, runs supervisor agent, and dispatches WhatsApp reply.
