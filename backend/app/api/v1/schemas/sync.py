from datetime import date, datetime

from pydantic import BaseModel


class SyncTriggerRequest(BaseModel):
    date_from: date | None = None
    date_to: date | None = None


class SyncTriggerResponse(BaseModel):
    sync_batch_id: str
    message: str


class SyncStatusResponse(BaseModel):
    batch_id: str
    sync_type: str
    status: str
    records_processed: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
