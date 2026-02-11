from datetime import date

from fastapi import APIRouter, Query

from app.api.v1.schemas.revenue import RevenueRow
from app.dependencies import SessionDep
from app.services.revenue_service import get_revenue

router = APIRouter(prefix="/revenue", tags=["revenue"])


@router.get("", response_model=list[RevenueRow])
async def list_revenue(
    session: SessionDep,
    branch_id: int = Query(default=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_revenue(session, branch_id, date_from, date_to)
