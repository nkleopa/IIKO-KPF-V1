from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailyRevenue


async def get_revenue(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> list[dict]:
    result = await session.execute(
        select(DailyRevenue)
        .where(
            and_(
                DailyRevenue.branch_id == branch_id,
                DailyRevenue.date >= date_from,
                DailyRevenue.date <= date_to,
            )
        )
        .order_by(DailyRevenue.date)
    )
    rows = result.scalars().all()
    return [
        {
            "date": r.date,
            "order_type": r.order_type,
            "order_type_detail": r.order_type_detail,
            "revenue_amount": r.revenue_amount,
            "order_count": r.order_count,
            "item_name": r.item_name,
            "item_quantity": r.item_quantity,
            "item_quantity_adjusted": r.item_quantity_adjusted,
        }
        for r in rows
    ]


async def get_revenue_totals(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> dict:
    """Aggregate revenue by order_type."""
    result = await session.execute(
        select(
            DailyRevenue.order_type,
            func.sum(DailyRevenue.revenue_amount).label("total"),
        )
        .where(
            and_(
                DailyRevenue.branch_id == branch_id,
                DailyRevenue.date >= date_from,
                DailyRevenue.date <= date_to,
            )
        )
        .group_by(DailyRevenue.order_type)
    )
    totals: dict[str, Decimal] = {}
    for row in result:
        totals[row.order_type] = row.total or Decimal("0")
    return totals


_KPF_TYPES = ["delivery", "hall"]


async def get_khinkali_count(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> Decimal:
    """Sum adjusted quantities for all khinkali items (delivery + hall only)."""
    result = await session.execute(
        select(func.sum(DailyRevenue.item_quantity_adjusted))
        .where(
            and_(
                DailyRevenue.branch_id == branch_id,
                DailyRevenue.date >= date_from,
                DailyRevenue.date <= date_to,
                DailyRevenue.item_name.ilike("%хинкали%"),
                DailyRevenue.order_type.in_(_KPF_TYPES),
            )
        )
    )
    return result.scalar() or Decimal("0")


UPSELL_PATTERNS = {
    "uzvar": "%узвар%",
    "sauce": "%соус%",
    "bread": "%хлеб шотис-пури%",
}


async def get_upsell_counts(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> dict[str, Decimal]:
    """Get quantity sold for each upsell category (delivery + hall only)."""
    counts: dict[str, Decimal] = {}
    for key, pattern in UPSELL_PATTERNS.items():
        result = await session.execute(
            select(func.sum(DailyRevenue.item_quantity))
            .where(
                and_(
                    DailyRevenue.branch_id == branch_id,
                    DailyRevenue.date >= date_from,
                    DailyRevenue.date <= date_to,
                    DailyRevenue.item_name.ilike(pattern),
                    DailyRevenue.order_type.in_(_KPF_TYPES),
                )
            )
        )
        counts[key] = result.scalar() or Decimal("0")
    return counts
