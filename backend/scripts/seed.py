"""
Database seed script — populates demo data.
Idempotent: safe to run multiple times.
Data is clearly labelled as sample/demo.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from datetime import date, datetime, timezone, timedelta
from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models import *  # noqa: F401, F403 — registers all tables

DEMO_PASSWORD = hash_password("Demo@1234")
ADMIN_PASSWORD = hash_password("Admin@1234")


async def seed():
    print("🌱 Seeding KisanSathi demo database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select, text
        existing = await db.execute(select(User).where(User.email == "admin@kisansathi.in"))
        if existing.scalar_one_or_none():
            print("✅ Already seeded — skipping (idempotent).")
            return

        # ── Admin ─────────────────────────────────────────────────────────────
        admin = User(
            email="admin@kisansathi.in",
            hashed_password=ADMIN_PASSWORD,
            role=UserRole.ADMIN,
            preferred_language="en",
            is_active=True,
            consent_given_at=datetime.now(timezone.utc),
        )
        db.add(admin)

        # ── Officer ───────────────────────────────────────────────────────────
        officer = User(
            email="officer@kvk.gov.in",
            phone="+919876543200",
            hashed_password=DEMO_PASSWORD,
            role=UserRole.OFFICER,
            preferred_language="gu",
            is_active=True,
            consent_given_at=datetime.now(timezone.utc),
        )
        db.add(officer)
        await db.flush()
        officer_profile = FarmerProfile(user_id=officer.id, full_name="Ramesh Patel", district="Surat", state="Gujarat", taluka="Olpad")
        db.add(officer_profile)

        # ── Farmers ───────────────────────────────────────────────────────────
        farmers_data = [
            {"phone": "+919876543210", "name": "Arjun Bhai Patel",   "district": "Surat",   "taluka": "Bardoli",  "lat": 21.12, "lon": 73.11, "crop": "cotton",    "soil": SoilType.BLACK, "irr": IrrigationType.DRIP},
            {"phone": "+919876543211", "name": "Leela Ben Desai",    "district": "Navsari", "taluka": "Navsari",  "lat": 20.95, "lon": 72.95, "crop": "groundnut",  "soil": SoilType.LOAM,  "irr": IrrigationType.RAINFED},
            {"phone": "+919876543212", "name": "Kantibhai Vasava",   "district": "Bharuch", "taluka": "Ankleshwar","lat": 21.63, "lon": 72.98, "crop": "wheat",      "soil": SoilType.CLAY,  "irr": IrrigationType.CANAL},
            {"phone": "+919876543213", "name": "Savita Ben Chauhan", "district": "Surat",   "taluka": "Mandvi",   "lat": 21.28, "lon": 73.29, "crop": "cotton",    "soil": SoilType.BLACK, "irr": IrrigationType.DRIP},
            {"phone": "+919876543214", "name": "Dhiraj Lal Prajapati","district": "Navsari","taluka": "Vansda",   "lat": 20.72, "lon": 73.37, "crop": "groundnut",  "soil": SoilType.SANDY, "irr": IrrigationType.SPRINKLER},
        ]

        # Master crops
        crops_data = [
            Crop(name_en="Cotton",    name_hi="कपास",    name_gu="કપાસ",    botanical_name="Gossypium hirsutum", category="Kharif"),
            Crop(name_en="Groundnut", name_hi="मूंगफली",  name_gu="મગફળી",  botanical_name="Arachis hypogaea",   category="Kharif"),
            Crop(name_en="Wheat",     name_hi="गेहूं",    name_gu="ઘઉં",     botanical_name="Triticum aestivum",  category="Rabi"),
            Crop(name_en="Rice",      name_hi="चावल",    name_gu="ચોખા",    botanical_name="Oryza sativa",       category="Kharif"),
            Crop(name_en="Sugarcane", name_hi="गन्ना",   name_gu="શેરડી",   botanical_name="Saccharum officinarum", category="Annual"),
        ]
        for c in crops_data:
            db.add(c)
        await db.flush()
        crop_map = {c.name_en.lower(): c for c in crops_data}

        created_farmers = []
        for fd in farmers_data:
            u = User(
                phone=fd["phone"],
                hashed_password=DEMO_PASSWORD,
                role=UserRole.FARMER,
                preferred_language="gu",
                is_active=True,
                consent_given_at=datetime.now(timezone.utc),
            )
            db.add(u)
            await db.flush()

            profile = FarmerProfile(user_id=u.id, full_name=fd["name"], district=fd["district"], taluka=fd["taluka"], state="Gujarat", onboarding_completed=True)
            db.add(profile)
            await db.flush()

            farm = Farm(farmer_profile_id=profile.id, name=f"{fd['name'].split()[0]}'s Farm",
                        latitude=fd["lat"], longitude=fd["lon"], area_hectares=3.5,
                        soil_type=fd["soil"], irrigation_type=fd["irr"])
            db.add(farm)
            await db.flush()

            # Farm crop
            crop_obj = crop_map.get(fd["crop"])
            if crop_obj:
                fc = FarmCrop(farm_id=farm.id, crop_id=crop_obj.id,
                              sowing_date=date(2024, 6, 15),
                              expected_harvest_date=date(2024, 10, 15),
                              current_stage=CropStage.VEGETATIVE,
                              area_hectares=3.5)
                db.add(fc)

            created_farmers.append((u, farm))

        await db.flush()

        # ── Sample Scans ──────────────────────────────────────────────────────
        scan_labels = ["Cotton Leaf Curl Virus", "Groundnut Early Leaf Spot", "Wheat Rust (Yellow)"]
        for i, (u, farm) in enumerate(created_farmers[:3]):
            scan = Scan(
                user_id=u.id, farm_id=farm.id,
                image_path=f"./uploads/sample/scan_{i+1}.jpg",
                predicted_label=scan_labels[i],
                confidence=0.85 + i * 0.03,
                severity=ScanSeverity.MEDIUM if i < 2 else ScanSeverity.HIGH,
                treatment_steps=["Remove infected plants", "Apply neem oil", "Consult KVK"],
                prevention_tips=["Use resistant variety", "Monitor weekly"],
                sources=[{"title": "ICAR Sample Guide", "is_sample": True}],
                is_mock=True,
            )
            db.add(scan)

        # ── Sample Alerts ─────────────────────────────────────────────────────
        alert_templates = [
            (AlertType.WEATHER, AlertSeverity.WARNING, "Heat Stress Alert", "Temperature forecast >38°C for 3 days. Ensure soil moisture for cotton."),
            (AlertType.PEST, AlertSeverity.CRITICAL, "Pink Bollworm Outbreak Reported", "Nearby farms in Bharuch report pink bollworm. Install pheromone traps."),
            (AlertType.PRICE, AlertSeverity.INFO, "Cotton Price Rising", "Modal price at Navsari mandi increased 4% this week. Good time to hold."),
            (AlertType.IRRIGATION, AlertSeverity.WARNING, "Irrigation Needed", "ET0 estimate: 40mm deficit. Apply drip irrigation within 48 hours."),
        ]
        for u, _ in created_farmers[:4]:
            for i, (atype, asev, title, body) in enumerate(alert_templates[:2]):
                db.add(Alert(user_id=u.id, alert_type=atype, severity=asev, title=title, body=body))

        # ── Sample Market Prices ──────────────────────────────────────────────
        from datetime import timedelta
        mandis = [
            ("Navsari", "Navsari", "cotton"),
            ("Surat",   "Surat",   "cotton"),
            ("Bharuch",  "Bharuch",  "wheat"),
            ("Junagadh", "Junagadh","groundnut"),
            ("Rajkot",  "Rajkot",  "groundnut"),
        ]
        base_prices = {"cotton": 6500, "wheat": 2200, "groundnut": 5000}
        import random; random.seed(42)
        for mandi, district, crop_name in mandis:
            for days_ago in range(30):
                d = date.today() - timedelta(days=days_ago)
                base = base_prices[crop_name]
                variation = random.randint(-200, 200)
                modal = base + variation + (days_ago * -5)  # slight downtrend going back
                db.add(MarketPrice(
                    mandi_name=mandi, district=district, state="Gujarat",
                    crop_name=crop_name, price_date=d,
                    min_price_inr=modal - 300, max_price_inr=modal + 300,
                    modal_price_inr=modal, unit="quintal", source="sample_csv",
                ))

        await db.commit()
        print("✅ Seed complete!")
        print("  Admin:   admin@kisansathi.in / Admin@1234")
        print("  Officer: officer@kvk.gov.in  / Demo@1234")
        print("  Farmer:  +919876543210       / Demo@1234")
        print("  (5 farmers, 3 scans, sample alerts, 30 days market prices)")
        print("  ⚠️  All data is sample/demo — not real farm data.")


if __name__ == "__main__":
    asyncio.run(seed())
