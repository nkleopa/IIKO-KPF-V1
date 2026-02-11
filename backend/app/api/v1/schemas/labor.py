from decimal import Decimal

from pydantic import BaseModel


class LaborRow(BaseModel):
    employee_name: str
    role_name: str | None = None
    total_hours: Decimal
    hourly_rate: Decimal
    labor_cost: Decimal
