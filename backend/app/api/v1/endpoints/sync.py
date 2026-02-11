import asyncio
from datetime import date, timedelta

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.api.v1.schemas.sync import (
    SyncStatusResponse,
    SyncTriggerRequest,
    SyncTriggerResponse,
)
from app.dependencies import SessionDep
from app.models import SyncLog
from app.services.iiko_client import IikoClient, IikoAuthError
from app.services.sync_service import daily_sync

router = APIRouter(prefix="/sync", tags=["sync"])


class IikoHealthResponse(BaseModel):
    server_reachable: bool
    licence_slots: str | None = None
    auth_ok: bool = False
    auth_error: str | None = None
    departments: list[dict] | None = None


@router.get("/health/iiko", response_model=IikoHealthResponse)
async def iiko_health_check():
    """Check iiko server connectivity, auth, and retrieve departments."""
    client = IikoClient()
    result = IikoHealthResponse(server_reachable=False)

    # Check licence (no auth needed)
    try:
        result.licence_slots = await client.check_licence()
        result.server_reachable = True
    except Exception:
        return result

    # Try full auth + department fetch
    try:
        async with client.session() as c:
            result.auth_ok = True
            result.departments = await c.get_departments()
    except IikoAuthError as e:
        result.auth_error = e.detail
    except Exception as e:
        result.auth_error = str(e)

    return result


@router.post("/trigger", response_model=SyncTriggerResponse)
async def trigger_sync(session: SessionDep, body: SyncTriggerRequest | None = None):
    """Manually trigger a sync. Defaults to yesterday if no dates provided."""
    target = None
    if body and body.date_from:
        target = body.date_from
    else:
        target = date.today() - timedelta(days=1)

    # Run sync in background task
    asyncio.create_task(daily_sync(target_date=target, sync_type="manual"))

    return SyncTriggerResponse(
        sync_batch_id="pending",
        message=f"Sync triggered for {target.isoformat()}",
    )


@router.get("/status", response_model=SyncStatusResponse | None)
async def sync_status(session: SessionDep):
    """Get latest sync log."""
    result = await session.execute(
        select(SyncLog).order_by(SyncLog.started_at.desc()).limit(1)
    )
    log = result.scalar_one_or_none()
    if not log:
        return None
    return SyncStatusResponse(
        batch_id=log.batch_id,
        sync_type=log.sync_type,
        status=log.status,
        records_processed=log.records_processed,
        error_message=log.error_message,
        started_at=log.started_at,
        completed_at=log.completed_at,
    )
