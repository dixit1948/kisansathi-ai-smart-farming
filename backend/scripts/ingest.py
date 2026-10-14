"""
Knowledge base ingestion script.
PDF/HTML/TXT -> clean -> chunk -> embed -> ChromaDB.
Real sources to load: ICAR, KVK, State Agri Dept, PlantVillage.
"""
import asyncio
import os
import sys
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import structlog
from app.core.config import settings
from app.rag.vector_store import get_vector_store

logger = structlog.get_logger(__name__)

CHUNK_SIZE = 600  # target tokens
CHUNK_OVERLAP = 100

# Sample documents — clearly labelled as demo content
SAMPLE_DOCUMENTS = [
    {
        "title": "Cotton Cultivation Guide — ICAR-CICR (Sample/Demo)",
        "source": "ICAR-CICR Cotton Guide (Sample)",
        "language": "en",
        "crop": "cotton",
        "topic": "cultivation",
        "is_sample": True,
        "text": """
Cotton Cultivation in Gujarat — Key Practices

SOIL AND CLIMATE: Cotton grows best in black cotton soil (vertisol) with good water retention.
Optimal temperature: 21-35°C. Requires 50-100cm rainfall or equivalent irrigation.

SOWING: Kharif season — June 10 to July 15. Delay beyond July 15 reduces yield by 20-30%.
Row spacing: 90cm x 45cm (hybrid). Seed rate: 2.5 kg/acre for hybrid varieties.
Recommended varieties for South Gujarat: NHH-44, RCH-2, Bunny BG-II.
Seed treatment: Thiram 4g/kg + Imidacloprid 5g/kg before sowing.

FERTILISER SCHEDULE: 
- Basal dose (at sowing): 20:40:40 NPK kg/ha + 5 tonnes FYM
- First top dressing (30 DAS): 40 kg N/ha (Urea 87 kg/ha)
- Second top dressing (60 DAS): 40 kg N/ha
- Micronutrient: Zinc sulphate 25 kg/ha if deficiency observed
Total NPK: 120:60:60 kg/ha

IRRIGATION: First irrigation: 10-12 DAS (if dry sowing). Critical stages: flowering (55-60 DAS),
boll development (80-100 DAS). ET0-based: apply when 50% field capacity depleted.
Drip irrigation saves 30-40% water vs flood.

WEED MANAGEMENT: Pre-emergence herbicide: Pendimethalin 1kg a.i./ha.
First hand weeding: 20-25 DAS. Second: 40-45 DAS.

HARVEST: First picking: 150-160 DAS when 50% bolls open. Continue every 15-20 days.
Avoid harvesting wet cotton (increases fungal risk). Target MCG (Moisture Content Grade) < 8%.

Source: ICAR-CICR, Nagpur — "Cotton Cultivation Technology" 2022 (SAMPLE for demo only)
Page 12-45. For real data see: https://cicr.org.in
""",
    },
    {
        "title": "Groundnut Advisory — KVK Gujarat (Sample/Demo)",
        "source": "KVK Advisory Gujarat (Sample)",
        "language": "en",
        "crop": "groundnut",
        "topic": "cultivation",
        "is_sample": True,
        "text": """
Groundnut Cultivation — KVK Navsari Advisory

VARIETIES: Kharif — GG-20, TG-51 (recommended for South Gujarat).
Rabi — GG-7, TAG-24.
Seed treatment: Thiram 3g/kg + Rhizobium culture + PSB.

SOWING: Kharif: June 15 – July 15. Row spacing: 30x10 cm (bunch), 45x15 cm (spreading).
Seed rate: 100 kg/ha (bunch), 80 kg/ha (spreading). Sowing depth: 5-7 cm.

NPK: 25:50:0 kg/ha basal. Top dress with Gypsum 400 kg/ha at pegging stage (45-50 DAS).
Do NOT apply excessive N — promotes vegetative growth at expense of pods.

IRRIGATION: Sandy loam soil — apply every 8-10 days in dry spell. Critical: pegging to pod fill.
Deficit irrigation (80% ETc) gives comparable yield with 20% water saving.

PEST/DISEASE: Leaf spot (Cercospora) — spray Mancozeb 0.2% at 30, 45, 60 DAS.
Tikka disease — same schedule + crop rotation with cereals.
Aphids — neem oil 5ml/L or Dimethoate 0.05%.

HARVEST: Kharif: Oct–Nov. Signs: inner shell has dark marks, leaves yellow. 
Thresh within 3 days of pulling to avoid aflatoxin.

Source: KVK Navsari, Gujarat Agri University (SAMPLE for demo only). 
Real source: https://www.nau.in
""",
    },
    {
        "title": "Wheat Cultivation — State Agriculture Dept Gujarat (Sample/Demo)",
        "source": "State Agri Dept Gujarat (Sample)",
        "language": "en",
        "crop": "wheat",
        "topic": "cultivation",
        "is_sample": True,
        "text": """
Wheat Cultivation in Gujarat — Rabi Season

SOWING: November 1-15 (timely sown), November 16-30 (late sown).
Late sowing reduces yield 20-25 kg/ha per day delay.
Variety recommendation: GW-496, GW-322 (South Gujarat). K-9107 (North Gujarat).
Seed rate: 100 kg/ha timely, 125 kg/ha late sown.
Seed treatment: Bavistin 2.5g/kg + Agrosan GN 2.5g/kg.

FERTILISER: Timely sown — 120:60:40 NPK kg/ha. Late sown — 100:50:40.
Apply full P, K and 50% N at sowing. Remaining 50% N at CRI stage (25 DAS).
Zinc deficiency common in Gujarat — apply ZnSO4 25 kg/ha.

IRRIGATION: 5-6 irrigations needed. Critical stages:
1. CRI (Crown Root Initiation) — 20-25 DAS: MOST CRITICAL
2. Tillering — 40-45 DAS
3. Jointing — 60-65 DAS
4. Flowering — 80-85 DAS
5. Milk stage — 100-105 DAS
6. Dough stage — 115-120 DAS
Do NOT irrigate during flowering (prevents poor setting).

PEST/DISEASE: Yellow rust — spray Propiconazole 0.1% if observed.
Aphids — appear in Feb-Mar, spray Dimethoate 0.03% if >10 aphids/ear.
Termite in sandy soils — chlorpyrifos 20EC 3L/ha in irrigation water.

HARVEST: April – when grain moisture 12-14%. Thresh immediately to avoid losses.
Target yield: 40-45 q/ha (timely sown).

Source: Director of Agriculture, Gujarat (SAMPLE for demo only).
Real data: https://agri.gujarat.gov.in
""",
    },
    {
        "title": "Common Pest & Disease Management — PlantVillage Summary (Sample/Demo)",
        "source": "PlantVillage Disease Database (Sample)",
        "language": "en",
        "crop": "general",
        "topic": "pest_disease",
        "is_sample": True,
        "text": """
Common Crop Diseases in Gujarat — Quick Reference

COTTON LEAF CURL VIRUS (CLCuV):
Symptoms: Upward/downward curling of leaves, dark green veins, small stunted leaves.
Cause: Begomovirus transmitted by whitefly (Bemisia tabaci).
Management: Remove infected plants. Imidacloprid 17.8 SL @ 0.5ml/L for whitefly.
Resistant varieties: RCH-2, Bunny. Yellow sticky traps 10/acre.
Never apply: systemic insecticides beyond recommended doses.

GROUNDNUT TIKKA (EARLY LEAF SPOT):
Symptoms: Brown circular spots with yellow halo on lower leaves (Cercospora arachidicola).
Management: Mancozeb 75WP @ 2g/L, spray at 30,45,60 DAS. Rotate with cereals.

WHEAT YELLOW RUST:
Symptoms: Yellow-orange pustules in stripes on leaves. Cool weather (10-15°C) favors.
Management: Propiconazole 25EC @ 0.1%, spray at flag leaf stage. Use resistant varieties.

BOLLWORM (Cotton):
Pink Bollworm: Shoot holes in bolls, pink larvae inside. Pheromone traps 10/ha.
American Bollworm: Large larvae eating into bolls. HNPV @ 250 LE/ha biological option.
Threshold: 1 moth/trap/night warrants spray.

DIAGNOSIS CONFIDENCE NOTE:
Confidence below 60% = request clearer photo in good daylight, from 30cm distance.
Focus on affected leaf. Avoid blur, shadows. Include healthy leaf for comparison.

Source: PlantVillage, Penn State University (SAMPLE summary for demo only).
Real database: https://plantvillage.psu.edu
""",
    },
]


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Simple sentence-aware chunker."""
    sentences = [s.strip() for s in text.replace("\n\n", ". ").split(". ") if s.strip()]
    chunks = []
    current = []
    current_len = 0

    for sent in sentences:
        word_count = len(sent.split())
        if current_len + word_count > chunk_size and current:
            chunks.append(". ".join(current) + ".")
            # Keep overlap
            overlap_sents = []
            overlap_len = 0
            for s in reversed(current):
                overlap_len += len(s.split())
                if overlap_len >= overlap:
                    break
                overlap_sents.insert(0, s)
            current = overlap_sents
            current_len = sum(len(s.split()) for s in current)
        current.append(sent)
        current_len += word_count

    if current:
        chunks.append(". ".join(current) + ".")
    return [c for c in chunks if len(c.split()) > 10]  # filter tiny chunks


async def ingest():
    print("📚 Ingesting knowledge documents into ChromaDB...")
    vs = get_vector_store()

    if vs._collection is None:
        print("⚠️  ChromaDB not available. Start with docker-compose up chroma first.")
        print("   Skipping ingestion — sample fallback will be used.")
        return

    total = 0
    for doc in SAMPLE_DOCUMENTS:
        chunks = _chunk_text(doc["text"])
        print(f"  {doc['title'][:60]} — {len(chunks)} chunks")
        documents = []
        for i, chunk in enumerate(chunks):
            doc_id = f"{doc['source'].replace(' ', '_')[:30]}_chunk_{i}_{uuid.uuid4().hex[:8]}"
            documents.append({
                "id": doc_id,
                "text": chunk,
                "metadata": {
                    "source": doc["source"],
                    "title": doc["title"],
                    "crop": doc.get("crop", "general"),
                    "topic": doc.get("topic", "general"),
                    "language": doc.get("language", "en"),
                    "is_sample": str(doc.get("is_sample", True)),
                    "chunk_index": str(i),
                },
            })
        count = await vs.add_documents(documents)
        total += count

    print(f"✅ Ingestion complete — {total} chunks added.")
    print("   ⚠️  All documents are sample data for demo. Load real ICAR/KVK PDFs for production.")
    print("   Real sources: https://cicr.org.in | https://www.nau.in | https://agri.gujarat.gov.in")


if __name__ == "__main__":
    asyncio.run(ingest())
