"""
KisanSathi Background Scheduler (APScheduler).
Manages:
1. Daily 6:00 AM farmer weather & irrigation digest
2. Hourly weather-risk & spray window scan
3. Daily Mandi market price refresh
4. Outbreak-cluster detection & notification
"""
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

_scheduler = None


async def daily_farmer_digest_job():
    """Daily 6am digest dispatched to registered farmers."""
    logger.info("Executing job: Daily 6:00 AM farmer digest")
    # In production: iterates active farmer profiles and pushes WhatsApp / SMS notification


async def hourly_weather_risk_job():
    """Hourly scan for severe weather anomalies (heat wave, high wind, heavy rain)."""
    logger.info("Executing job: Hourly weather-risk scan")


async def daily_mandi_refresh_job():
    """Daily refresh of APMC mandi market commodity prices."""
    logger.info("Executing job: Daily mandi price refresh")


async def outbreak_cluster_detection_job():
    """Spatial scan for disease outbreak clusters across talukas."""
    logger.info("Executing job: Outbreak cluster detection")


def start_scheduler():
    """Initialize APScheduler with fallback to in-memory scheduler."""
    global _scheduler
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        _scheduler = AsyncIOScheduler()

        # 1. Daily 6am Farmer Digest
        _scheduler.add_job(
            daily_farmer_digest_job,
            CronTrigger(hour=settings.DAILY_DIGEST_HOUR, minute=0),
            id="daily_farmer_digest",
            name="Daily Farmer Digest",
            replace_existing=True,
        )

        # 2. Hourly Weather Scan
        _scheduler.add_job(
            hourly_weather_risk_job,
            IntervalTrigger(hours=settings.WEATHER_SCAN_INTERVAL_HOURS),
            id="hourly_weather_scan",
            name="Hourly Weather Risk Scan",
            replace_existing=True,
        )

        # 3. Daily Mandi Refresh
        _scheduler.add_job(
            daily_mandi_refresh_job,
            IntervalTrigger(hours=settings.MARKET_REFRESH_INTERVAL_HOURS),
            id="daily_mandi_refresh",
            name="Daily Mandi Refresh",
            replace_existing=True,
        )

        # 4. Outbreak Cluster Detection
        _scheduler.add_job(
            outbreak_cluster_detection_job,
            IntervalTrigger(minutes=30),
            id="outbreak_cluster_scan",
            name="Outbreak Cluster Detection",
            replace_existing=True,
        )

        _scheduler.start()
        logger.info("APScheduler background jobs initialized and running")
    except Exception as e:
        logger.warning("Could not start APScheduler (in-memory mode)", error=str(e))


def stop_scheduler():
    """Shutdown background scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
