from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class WriteoffRow(BaseModel):
    date: date
    article_name: str
    category: str
    amount: Decimal


class WriteoffSummaryRow(BaseModel):
    category: str
    total_amount: Decimal
