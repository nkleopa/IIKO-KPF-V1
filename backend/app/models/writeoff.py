from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin


class Writeoff(TimestampMixin, Base):
    __tablename__ = "writeoffs"
    __table_args__ = (
        Index("ix_writeoffs_branch_date", "branch_id", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    date: Mapped[date]
    article_name: Mapped[str] = mapped_column(String(255))  # product UUID (legacy)
    category: Mapped[str] = mapped_column(String(64))  # mapped: spoilage/marketing/promo/...
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    document_number: Mapped[str | None] = mapped_column(String(64))
    account_name: Mapped[str | None] = mapped_column(String(255))
    product_name: Mapped[str | None] = mapped_column(String(255))
    item_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    sync_batch_id: Mapped[str | None] = mapped_column(String(64))

    branch: Mapped["Branch"] = relationship(back_populates="writeoffs")  # noqa: F821
