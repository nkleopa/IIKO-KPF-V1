import asyncio
from datetime import date

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.v1.schemas.waiter_checks import WaiterCheckRow
from app.dependencies import SessionDep
from app.services.waiter_check_service import get_waiter_checks
from app.services.sync_service import sync_waiter_checks

router = APIRouter(prefix="/waiter-checks", tags=["waiter-checks"])


@router.get("", response_model=list[WaiterCheckRow])
async def list_waiter_checks(
    session: SessionDep,
    branch_id: int = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_waiter_checks(session, branch_id, date_from, date_to)


class SyncResponse(BaseModel):
    message: str
    results: dict[str, int] | None = None


@router.post("/sync", response_model=SyncResponse)
async def trigger_waiter_checks_sync(
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    """Trigger waiter checks sync for all Rostov branches."""
    results = await sync_waiter_checks(date_from, date_to)
    total = sum(results.values())
    return SyncResponse(
        message=f"Synced {total} waiter check records",
        results=results,
    )
