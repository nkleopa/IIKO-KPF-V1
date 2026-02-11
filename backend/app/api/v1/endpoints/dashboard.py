from datetime import date

from fastapi import APIRouter, Query

from app.api.v1.schemas.dashboard import KPFResponse
from app.dependencies import SessionDep
from app.services.kpf_service import get_kpf

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpf", response_model=KPFResponse)
async def dashboard_kpf(
    session: SessionDep,
    branch_id: int = Query(default=1),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    return await get_kpf(session, branch_id, date_from, date_to)
