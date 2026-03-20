import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class TestResult(Base):
    """A single test result from a lab report."""

    __tablename__ = "test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lab_report_id: Mapped[str] = mapped_column(String(36), ForeignKey("lab_reports.id"), nullable=False, index=True)
    family_member_id: Mapped[str] = mapped_column(String(36), ForeignKey("family_members.id"), nullable=False, index=True)
    analyte_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyte_catalog.id"), nullable=False, index=True)

    # Denormalized report_date for time-series query optimization
    report_date: Mapped[datetime | None] = mapped_column(Date, nullable=True, index=True)

    # Raw values (preserved for re-canonicalization)
    raw_name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    # Canonical values
    canonical_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    canonical_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    # Reference range (from reference_ranges table at time of extraction)
    ref_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    ref_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    ref_source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Flags
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_out_of_range: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    lab_report = relationship("LabReport", back_populates="test_results", lazy="raise")
    family_member = relationship("FamilyMember", back_populates="test_results", lazy="raise")
    analyte = relationship("AnalyteCatalog", back_populates="test_results", lazy="raise")
