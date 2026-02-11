from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class Branch(TimestampMixin, Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    iiko_department_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    territory: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    revenues: Mapped[list["DailyRevenue"]] = relationship(back_populates="branch")  # noqa: F821
    attendances: Mapped[list["EmployeeAttendance"]] = relationship(back_populates="branch")  # noqa: F821
    staff_rates: Mapped[list["StaffRate"]] = relationship(back_populates="branch")  # noqa: F821
    writeoffs: Mapped[list["Writeoff"]] = relationship(back_populates="branch")  # noqa: F821
