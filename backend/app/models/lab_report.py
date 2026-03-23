import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from ..database import Base


class ExtractionStatus(str, enum.Enum):
    """Status of PDF extraction."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    PARTIAL = "partial"  # Some fields extracted, some failed
    FAILED = "failed"


class LabReport(Base):
    """A single lab report PDF."""

    __tablename__ = "lab_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_member_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("family_members.id"), nullable=False, index=True
    )
    uploaded_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_date: Mapped[datetime | None] = mapped_column(Date, nullable=True, index=True)
    lab_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extractor_used: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g., "GenericPDFExtractor"
    extraction_status: Mapped[str] = mapped_column(
        SQLEnum(ExtractionStatus),
        default=ExtractionStatus.PENDING,
        nullable=False,
        index=True,
    )
    extraction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    raw_patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    family_member = relationship("FamilyMember", back_populates="lab_reports", lazy="raise")
    uploaded_by_user = relationship("User", back_populates="lab_reports", lazy="raise")
    test_results = relationship(
        "TestResult", back_populates="lab_report", cascade="all, delete-orphan", lazy="raise"
    )
