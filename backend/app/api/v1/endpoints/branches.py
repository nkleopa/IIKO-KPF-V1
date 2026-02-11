from fastapi import APIRouter
from sqlalchemy import select

from app.api.v1.schemas.branch import BranchResponse
from app.dependencies import SessionDep
from app.models import Branch

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=list[BranchResponse])
async def list_branches(session: SessionDep):
    result = await session.execute(
        select(Branch).where(Branch.is_active.is_(True)).order_by(Branch.name)
    )
    return [
        BranchResponse(
            id=b.id,
            name=b.name,
            city=b.city,
            territory=b.territory,
            is_active=b.is_active,
        )
        for b in result.scalars().all()
    ]
