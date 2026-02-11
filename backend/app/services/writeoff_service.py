from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Writeoff


async def get_writeoffs(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> list[dict]:
    result = await session.execute(
        select(Writeoff)
        .where(
            and_(
                Writeoff.branch_id == branch_id,
                Writeoff.date >= date_from,
                Writeoff.date <= date_to,
            )
        )
        .order_by(Writeoff.date)
    )
    return [
        {
            "date": r.date,
            "article_name": r.article_name,
            "category": r.category,
            "amount": r.amount,
        }
        for r in result.scalars().all()
    ]


async def get_writeoff_summary(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> list[dict]:
    result = await session.execute(
        select(
            Writeoff.category,
            func.sum(Writeoff.amount).label("total_amount"),
        )
        .where(
            and_(
                Writeoff.branch_id == branch_id,
                Writeoff.date >= date_from,
                Writeoff.date <= date_to,
            )
        )
        .group_by(Writeoff.category)
    )
    return [
        {"category": row.category, "total_amount": row.total_amount or Decimal("0")}
        for row in result
    ]


async def get_writeoff_total(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> Decimal:
    result = await session.execute(
        select(func.sum(Writeoff.amount))
        .where(
            and_(
                Writeoff.branch_id == branch_id,
                Writeoff.date >= date_from,
                Writeoff.date <= date_to,
            )
        )
    )
    return result.scalar() or Decimal("0")
