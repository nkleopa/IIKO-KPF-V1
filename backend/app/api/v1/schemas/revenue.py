from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RevenueRow(BaseModel):
    date: date
    order_type: str
    order_type_detail: str
    revenue_amount: Decimal
    order_count: int
    item_name: str | None = None
    item_quantity: Decimal | None = None
    item_quantity_adjusted: Decimal | None = None
