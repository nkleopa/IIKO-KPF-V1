from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class StaffRate(TimestampMixin, Base):
    """SCD Type 2: tracks hourly rate history per employee."""

    __tablename__ = "staff_rates"
    __table_args__ = (
        Index("ix_staff_rates_employee_current", "employee_id", "is_current"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(64))  # business key
    employee_name: Mapped[str] = mapped_column(String(255))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    version: Mapped[int] = mapped_column(default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_from: Mapped[date]
    valid_to: Mapped[date | None]  # NULL = current

    branch: Mapped["Branch"] = relationship(back_populates="staff_rates")  # noqa: F821
