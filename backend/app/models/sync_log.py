from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin


class SyncLog(TimestampMixin, Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(64), unique=True)
    sync_type: Mapped[str] = mapped_column(String(32))  # daily / manual
    status: Mapped[str] = mapped_column(String(16))  # running / success / failed
    records_processed: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime]
    completed_at: Mapped[datetime | None]
