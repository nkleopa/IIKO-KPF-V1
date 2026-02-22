from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class WaiterCheckRow(BaseModel):
    date: date
    waiter_name: str
    check_count: int
    revenue: Decimal
    avg_check: Decimal
