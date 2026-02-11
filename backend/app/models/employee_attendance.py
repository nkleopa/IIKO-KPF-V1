from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class EmployeeAttendance(TimestampMixin, Base):
    __tablename__ = "employee_attendance"
    __table_args__ = (
        Index("ix_attendance_branch_date", "branch_id", "date_from"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    iiko_attendance_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    employee_id: Mapped[str] = mapped_column(String(64))
    employee_name: Mapped[str | None] = mapped_column(String(255))
    role_id: Mapped[str | None] = mapped_column(String(64))
    role_name: Mapped[str | None] = mapped_column(String(128))
    date_from: Mapped[datetime]
    date_to: Mapped[datetime | None]
    worked_minutes: Mapped[int] = mapped_column(default=0)
    worked_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0)
    iiko_payment_sum: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    sync_batch_id: Mapped[str | None] = mapped_column(String(64))

    branch: Mapped["Branch"] = relationship(back_populates="attendances")  # noqa: F821
