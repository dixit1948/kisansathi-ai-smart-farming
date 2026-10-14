# KisanSathi — Information Architecture

## 1. Site Map & Navigation Hierarchy

```
KisanSathi App Root
├── Public / Authentication
│   ├── / (Landing Page with Value Props & Quick Demo)
│   ├── /login (Phone OTP login + Email password fallback)
│   └── /onboarding (4-Step Farm Setup Wizard)
│
├── Farmer Experience (Role: Farmer)
│   ├── /dashboard (Farm Overview: Weather, Today's Task, Irrigation, Alerts, Quick Actions)
│   ├── /chat (AI Chat: Multi-turn, Voice input, Image attach, Source chips, "Why this advice?")
│   ├── /scan (Disease Scan: Camera upload, Preview/Crop, Diagnosis card, History gallery)
│   ├── /calendar (Crop Calendar: Stage timeline, Tasks, Weather overlay)
│   ├── /market (Market Insights: Price table, Trend line chart, Sell/Hold badge, Mandis)
│   ├── /alerts (Alerts Center: Rain/Heat/Pest/Price notifications with filter & read state)
│   └── /settings (Language switcher, Profile, Consent & Data export/delete)
│
├── Officer Experience (Role: Officer)
│   ├── /officer (District Overview, Map with pest risk markers & outbreak clusters, CSV Export)
│   └── /officer/farmer/:id (Specific farmer crop profile & scan history)
│
├── Demonstration & System Trace (All / Judges / Admin)
│   ├── /trace (Agent Trace: Live timeline of Supervisor + 4 Agents, latencies, tokens, RAG chunks)
│   └── /admin (System stats, model parameters, mock mode toggles)
│
└── System & Error Pages
    ├── /404 (Not Found with back home action)
    ├── /500 (Server Error with retry action)
    └── Offline Banner (PWA service worker connectivity state)
```

## 2. Global Navigation Rules
- **Mobile First Bottom Navigation Bar:**
  1. Home (`/dashboard`)
  2. Ask AI (`/chat`)
  3. Scan Leaf (`/scan`) — Floating prominent center green action button
  4. Market (`/market`)
  5. More / Calendar (`/calendar` & `/alerts` indicator)
- **Top Bar:** Brand logo + Offline indicator + Language quick toggle (EN / HI / GU) + Profile avatar / role pill.
- **Officer View Toggle:** If user role is `OFFICER` or `ADMIN`, a badge in top header allows instant switching to Extension Officer map view.
- **Max 3 Taps Rule:** Any primary task (Take scan, ask query, check today's price) is accessible in ≤ 2 taps from anywhere in the app.
