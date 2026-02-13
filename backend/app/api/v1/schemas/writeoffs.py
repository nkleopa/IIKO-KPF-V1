from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class WriteoffRow(BaseModel):
    date: date
    document_number: str | None = None
    account_name: str | None = None
    product_name: str | None = None
    item_quantity: Decimal | None = None
    category: str
    amount: Decimal


class WriteoffSummaryRow(BaseModel):
    category: str
    total_amount: Decimal
