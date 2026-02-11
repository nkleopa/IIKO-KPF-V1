from datetime import date

from fastapi import APIRouter, Query

from app.api.v1.schemas.labor import LaborRow
from app.dependencies import SessionDep
from app.services.labor_service import get_labor

router = APIRouter(prefix="/labor", tags=["labor"])


@router.get("", response_model=list[LaborRow])
async def list_labor(
    session: SessionDep,
    branch_id: int = Query(default=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_labor(session, branch_id, date_from, date_to)
