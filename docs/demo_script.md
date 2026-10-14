# KisanSathi — 3-Minute Demo Script (for Hackathon Judges & Evaluators)

**Audience:** Judges, Agricultural Extension Officers, Tech Leads.
**Total Duration:** 3 minutes (180 seconds).

---

## Act 1: The Problem & Farmer Onboarding (0:00 - 0:45)
- **Presenter says:**
  > "Meet Arjun Bhai, a cotton farmer in Bardoli, Gujarat. Like millions of Indian farmers, his crops face sudden pest attacks, unpredictable rains, and volatile mandi prices. Government advice is often generic, delayed, and written in complex English."
- **Screen Action:**
  1. Open `http://localhost:3000`. Show the landing page with Gujarati/Hindi/English language selector.
  2. Click **"Demo Login (Farmer: Arjun Bhai)"** (or simulate rapid 4-step onboarding).
  3. Land on **Farm Overview Dashboard**. Point out:
     - Today's Weather & ET0 Irrigation need: *"Water tomorrow for 2 hours (Drip); avoid spraying today due to wind."*
     - Task of the Day: *"Day 45: Apply split dose urea."*
     - Active Outbreak Alert: *"Pink Bollworm reported nearby in Bharuch."*

---

## Act 2: Golden Path — Leaf Scan Diagnosis in < 10s (0:45 - 1:30)
- **Presenter says:**
  > "Arjun notices curling leaves on his cotton plant. Instead of waiting days for an expert visit, he opens KisanSathi's Disease Scan."
- **Screen Action:**
  1. Click **"Scan Leaf"** in bottom navigation.
  2. Select sample leaf photo (`sample/scan_1.jpg`).
  3. Click **"Analyze Leaf"**.
  4. In < 2 seconds, result appears:
     - **Disease:** Cotton Leaf Curl Virus (CLCuV)
     - **Confidence:** 87%
     - **Severity:** Medium
     - **Treatment:** Step 1 Organic first (Neem oil spray 5ml/L + rogue infected plants); Step 2 Chemical caution (Imidacloprid 17.8 SL with safe harvesting interval).
     - **Verified Citation:** ICAR-CICR Cotton Bulletin.
  5. Click **"Ask AI follow-up"** -> transitions smoothly into AI Chat with pre-populated context.

---

## Act 3: Multi-Agent Chat & Market Intelligence (1:30 - 2:15)
- **Presenter says:**
  > "Behind the scenes, KisanSathi runs a LangGraph Multi-Agent Supervisor powered by IBM Granite on watsonx.ai. Let's ask a combined question in Gujarati."
- **Screen Action:**
  1. In Chat, select Gujarati or type: *"આજે કપાસનો ભાવ શું છે અને વેચવો જોઈએ કે નહીં?"* (What is cotton price today and should I sell?)
  2. Hit Send.
  3. Response appears instantly with:
     - Navsari Mandi modal rate (₹6,850/quintal, +4% trend).
     - Actionable Advice: Hold stock for 7-10 days if storage is available.
     - Source cited: Agmarknet APMC Navsari.
  4. Expand **"Why this advice?"** -> Shows agent breakdown (`market_insights` agent triggered, latency 95ms).

---

## Act 4: Extension Officer View & Agent Trace (2:15 - 3:00)
- **Presenter says:**
  > "Now let's switch to the Krishi Vigyan Kendra extension officer view. While farmers get localized advice, officers get a geospatial view of outbreak clusters."
- **Screen Action:**
  1. Navigate to `/officer`.
  2. Show the interactive Leaflet map:
     - Point out the red outbreak cluster in Bardoli (14 Pink Bollworm detections).
     - Show the one-click action: "Dispatch Taluka Advisory".
     - Click **"Export CSV"** to demonstrate government data integration.
  3. Navigate to `/trace` (Judge Mode):
     - Show the live LangGraph supervisor trace: Intent classification -> Parallel Agent execution -> IBM Granite response merging -> Latency breakdown.
- **Presenter concludes:**
  > "KisanSathi bridges the last-mile agricultural advisory gap: fast, multimodal, localized, safe, and built end-to-end on IBM Granite and watsonx.ai."
