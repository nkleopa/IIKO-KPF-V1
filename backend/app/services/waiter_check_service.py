from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.waiter_check import WaiterCheck


async def get_waiter_checks(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> list[dict]:
    result = await session.execute(
        select(WaiterCheck)
        .where(
            and_(
                WaiterCheck.branch_id == branch_id,
                WaiterCheck.date >= date_from,
                WaiterCheck.date <= date_to,
            )
        )
        .order_by(WaiterCheck.date, WaiterCheck.waiter_name)
    )
    return [
        {
            "date": r.date,
            "waiter_name": r.waiter_name,
            "check_count": r.check_count,
            "revenue": r.revenue,
            "avg_check": r.avg_check,
        }
        for r in result.scalars().all()
    ]
