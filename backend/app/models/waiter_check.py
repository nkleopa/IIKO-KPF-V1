from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class WaiterCheck(TimestampMixin, Base):
    __tablename__ = "waiter_checks"
    __table_args__ = (
        UniqueConstraint("branch_id", "date", "waiter_name", name="uq_waiter_checks_branch_date_waiter"),
        Index("ix_waiter_checks_branch_date", "branch_id", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    date: Mapped[date]
    waiter_name: Mapped[str] = mapped_column(String(255))
    check_count: Mapped[int] = mapped_column(default=0)
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    avg_check: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    branch: Mapped["Branch"] = relationship()  # noqa: F821
