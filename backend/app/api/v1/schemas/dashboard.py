from decimal import Decimal

from pydantic import BaseModel


class UpsellData(BaseModel):
    uzvar_qty: Decimal = Decimal("0")
    sauce_qty: Decimal = Decimal("0")
    bread_qty: Decimal = Decimal("0")


class KPFResponse(BaseModel):
    revenue_total: Decimal
    revenue_delivery: Decimal
    revenue_hall: Decimal
    labor_cost_total: Decimal
    kitchen_labor_cost: Decimal = Decimal("0")
    hall_labor_cost: Decimal = Decimal("0")
    writeoff_total: Decimal
    lc_percent: Decimal
    kc_percent: Decimal
    khinkali_count: Decimal = Decimal("0")
    upsells: UpsellData | None = None
    cogs_percent: Decimal | None = None
