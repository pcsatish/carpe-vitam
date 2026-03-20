import uuid
from sqlalchemy import String, Boolean, Text, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AnalyteCatalog(Base):
    """Catalog of all known lab tests/analytes."""

    __tablename__ = "analyte_catalog"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Lipid, Liver, Renal, Thyroid, etc.
    canonical_unit: Mapped[str] = mapped_column(String(50), nullable=False)  # mg/dL, U/L, etc.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_analyte_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String(36)), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    aliases = relationship("AnalyteAlias", back_populates="analyte", cascade="all, delete-orphan", lazy="raise")
    reference_ranges = relationship("ReferenceRange", back_populates="analyte", cascade="all, delete-orphan", lazy="raise")
    test_results = relationship("TestResult", back_populates="analyte", lazy="raise")


class AnalyteAlias(Base):
    """Raw test names that map to canonical analytes."""

    __tablename__ = "analyte_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analyte_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyte_catalog.id"), nullable=False, index=True)
    raw_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lab_source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "Thyrocare", "Redcliffe", or None for generic

    # Relationships
    analyte = relationship("AnalyteCatalog", back_populates="aliases", lazy="raise")

    __table_args__ = (
        # Unique constraint: (raw_name, lab_source)
    )


class ReferenceRange(Base):
    """Reference ranges for analytes by sex and age."""

    __tablename__ = "reference_ranges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analyte_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyte_catalog.id"), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    low_normal: Mapped[float | None] = mapped_column(nullable=True)
    high_normal: Mapped[float | None] = mapped_column(nullable=True)
    low_critical: Mapped[float | None] = mapped_column(nullable=True)
    high_critical: Mapped[float | None] = mapped_column(nullable=True)
    sex: Mapped[str | None] = mapped_column(String(10), nullable=True)  # M, F, or None for all
    age_min_years: Mapped[int | None] = mapped_column(nullable=True)
    age_max_years: Mapped[int | None] = mapped_column(nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Lab name or URL

    # Relationships
    analyte = relationship("AnalyteCatalog", back_populates="reference_ranges", lazy="raise")
