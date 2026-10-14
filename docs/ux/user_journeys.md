# KisanSathi — User Journeys

## Journey 1: Farmer Rapid Leaf Scan & Disease Treatment (Critical Golden Path)
**Goal:** Arjun discovers curling yellow leaves on his cotton crop and gets actionable cure in <10 seconds.

```mermaid
journey
    title Farmer Disease Diagnosis Flow
    section Discovery
      Notices yellow curling leaves on cotton: 5: Farmer
      Opens KisanSathi PWA or WhatsApp: 5: Farmer
    section Action
      Taps camera button (Scan Leaf): 5: Farmer
      Takes leaf photo in sunlight: 4: Farmer
      Submits scan: 5: Farmer
    section AI Analysis
      Pest & Disease Agent classifies (CLCuV): 5: System
      Supervisor verifies confidence & sources: 5: System
    section Outcome
      Receives diagnosis in Gujarati with severity bar: 5: Farmer
      Views Organic Neem solution first, chemical caution second: 5: Farmer
      Shares treatment via WhatsApp or saves to history: 5: Farmer
```

**Steps:**
1. **Entry:** Farmer taps "Scan Leaf" tile on Farm Overview (or sends image to WhatsApp bot).
2. **Capture/Preview:** Camera interface opens with overlay frame. Client compresses image (<1MB) and strips EXIF GPS data for privacy.
3. **Execution:** Multimodal Pest & Disease Agent predicts condition ("Cotton Leaf Curl Virus", 87% confidence, Medium Severity).
4. **Presentation:** High-contrast card with:
   - Clear disease name in farmer's language (કપાસ પર્ણ વલન વાયરસ).
   - Visual severity badge (Amber / Medium).
   - Step 1: Immediate physical quarantine (remove affected plant).
   - Step 2: Organic-first remedy (Neem oil spray 5ml/L).
   - Step 3: Chemical caution (Imidacloprid 17.8 SL @ 0.5 ml/L, ICAR citation).
5. **Follow-up:** One-tap action "Ask AI Question about this leaf" opens chat with pre-filled context.

---

## Journey 2: Onboarding & Farm Setup (First-Time User)
**Goal:** Setup farm profile in 4 steps within 90 seconds without typing tedious forms.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer
    participant UI as Onboarding Wizard
    participant API as KisanSathi Backend
    participant DB as Database

    Farmer->>UI: Selects Language (Gujarati/Hindi/English)
    UI->>Farmer: Updates entire UI instantly to selected language
    Farmer->>UI: Step 2: Pin location on map (or Auto-detect GPS)
    UI->>API: Reverse geocode to Taluka & District (Surat/Bardoli)
    Farmer->>UI: Step 3: Select Crops (Cotton, Sugarcane) & Area (3.5 ha)
    Farmer->>UI: Step 4: Pick Soil (Black Soil) & Irrigation (Drip)
    Farmer->>UI: Taps "Complete Farm Setup"
    UI->>API: POST /api/v1/farms
    API->>DB: Store profile, farm & crop associations
    API-->>UI: 201 Created & trigger initial weather forecast
    UI->>Farmer: Redirect to personalized Farm Overview Dashboard
```

---

## Journey 3: Agri Extension Officer Outbreak Monitoring & Triage
**Goal:** Officer Ramesh tracks pest hot-spots across 3 districts and issues early advisories.

1. **Dashboard Entry:** Officer logs in with Gov/KVK credentials. Navigates to `/officer`.
2. **Spatial Risk Map:** Interactive Leaflet map renders farms and scan clusters with color-coded risk markers (Red: high pest density, Amber: moderate, Green: healthy).
3. **Cluster Investigation:** Clicks a cluster in Bardoli; sees 14 recent scans of Pink Bollworm within 5km radius.
4. **Action:** Clicks "Dispatch Taluka Advisory" -> Sends automated advisory to all farmers registered with Cotton in Bardoli.
5. **Export:** Clicks "Export Incident CSV" for weekly report to District Agriculture Officer.
