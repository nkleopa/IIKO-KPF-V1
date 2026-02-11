from datetime import date

from pydantic import BaseModel


class DateRangeParams(BaseModel):
    branch_id: int = 1
    date_from: date
    date_to: date
