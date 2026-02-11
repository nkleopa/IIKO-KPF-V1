from datetime import date

from fastapi import APIRouter, Query

from app.api.v1.schemas.writeoffs import WriteoffRow, WriteoffSummaryRow
from app.dependencies import SessionDep
from app.services.writeoff_service import get_writeoff_summary, get_writeoffs

router = APIRouter(prefix="/writeoffs", tags=["writeoffs"])


@router.get("", response_model=list[WriteoffRow])
async def list_writeoffs(
    session: SessionDep,
    branch_id: int = Query(default=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_writeoffs(session, branch_id, date_from, date_to)


@router.get("/summary", response_model=list[WriteoffSummaryRow])
async def writeoff_summary(
    session: SessionDep,
    branch_id: int = Query(default=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_writeoff_summary(session, branch_id, date_from, date_to)
