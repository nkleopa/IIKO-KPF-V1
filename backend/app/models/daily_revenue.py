from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class DailyRevenue(TimestampMixin, Base):
    __tablename__ = "daily_revenue"
    __table_args__ = (
        Index("ix_daily_revenue_branch_date", "branch_id", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    date: Mapped[date]
    order_type: Mapped[str] = mapped_column(String(32))  # delivery / hall / excluded
    order_type_detail: Mapped[str] = mapped_column(String(128))  # original iiko value
    revenue_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    order_count: Mapped[int] = mapped_column(default=0)
    item_name: Mapped[str | None] = mapped_column(String(255))
    item_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    item_quantity_adjusted: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    sync_batch_id: Mapped[str | None] = mapped_column(String(64))

    branch: Mapped["Branch"] = relationship(back_populates="revenues")  # noqa: F821
