from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.labor_service import get_kitchen_labor_total, get_labor_total
from app.services.revenue_service import (
    get_khinkali_count,
    get_revenue_totals,
    get_upsell_counts,
)
from app.services.writeoff_service import get_writeoff_total


async def get_kpf(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> dict:
    revenue_by_type = await get_revenue_totals(session, branch_id, date_from, date_to)
    labor_total = await get_labor_total(session, branch_id, date_from, date_to)
    kitchen_labor_total = await get_kitchen_labor_total(session, branch_id, date_from, date_to)
    writeoff_total = await get_writeoff_total(session, branch_id, date_from, date_to)
    khinkali = await get_khinkali_count(session, branch_id, date_from, date_to)
    upsells = await get_upsell_counts(session, branch_id, date_from, date_to)

    revenue_delivery = revenue_by_type.get("delivery", Decimal("0"))
    revenue_hall = revenue_by_type.get("hall", Decimal("0"))
    revenue_total = revenue_delivery + revenue_hall

    lc_percent = Decimal("0")
    kc_percent = Decimal("0")
    if revenue_total > 0:
        # LC% = Total_Labor_Cost / Total_Revenue × 100
        lc_percent = (labor_total / revenue_total * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        # KC% = Kitchen_Labor_Cost / Total_Revenue × 100
        kc_percent = (kitchen_labor_total / revenue_total * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

    return {
        "revenue_total": revenue_total,
        "revenue_delivery": revenue_delivery,
        "revenue_hall": revenue_hall,
        "labor_cost_total": labor_total,
        "kitchen_labor_cost": kitchen_labor_total,
        "writeoff_total": writeoff_total,
        "lc_percent": lc_percent,
        "kc_percent": kc_percent,
        "khinkali_count": khinkali,
        "upsells": {
            "uzvar_qty": upsells.get("uzvar", Decimal("0")),
            "sauce_qty": upsells.get("sauce", Decimal("0")),
            "bread_qty": upsells.get("bread", Decimal("0")),
        },
    }
