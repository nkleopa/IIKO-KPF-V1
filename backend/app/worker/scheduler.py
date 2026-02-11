from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.logger import logger

scheduler = AsyncIOScheduler()


def start_scheduler():
    from app.worker.tasks.daily_sync import run_daily_sync

    scheduler.add_job(
        run_daily_sync,
        trigger=CronTrigger(hour=settings.SYNC_HOUR, minute=settings.SYNC_MINUTE),
        id="daily_sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started. Daily sync at {settings.SYNC_HOUR:02d}:{settings.SYNC_MINUTE:02d}"
    )


def shutdown_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down.")
