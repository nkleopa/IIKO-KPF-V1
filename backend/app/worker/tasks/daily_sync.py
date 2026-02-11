from app.core.logger import logger
from app.services.sync_service import daily_sync


async def run_daily_sync():
    """Scheduled task: sync yesterday's data from iiko."""
    try:
        await daily_sync(target_date=None, sync_type="daily")
    except Exception as e:
        logger.error(f"Scheduled daily sync failed: {e}")
