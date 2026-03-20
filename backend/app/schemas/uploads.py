"""Upload schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class LabReportSchema(BaseModel):
    """Lab report response."""

    id: str
    family_member_id: str
    original_filename: str
    report_date: datetime | None
    lab_name: str | None
    extraction_status: str
    extraction_notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResponseSchema(BaseModel):
    """Response after uploading a file."""

    lab_report_id: str
    extraction_status: str
    message: str
