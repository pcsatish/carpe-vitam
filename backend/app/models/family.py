import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from ..database import Base


class Family(Base):
    """Family/group model."""

    __tablename__ = "families"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="families", foreign_keys=[created_by], lazy="raise")
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan", lazy="raise")


class FamilyMemberRole(str, enum.Enum):
    """Role of a family member."""

    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class FamilyMember(Base):
    """Member of a family (user or dependent)."""

    __tablename__ = "family_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.id"), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)  # M, F, Other
    role: Mapped[str] = mapped_column(SQLEnum(FamilyMemberRole), default=FamilyMemberRole.MEMBER, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    family = relationship("Family", back_populates="members", lazy="raise")
    user = relationship("User", back_populates="family_members", foreign_keys=[user_id], lazy="raise")
    lab_reports = relationship("LabReport", back_populates="family_member", lazy="raise")
    test_results = relationship("TestResult", back_populates="family_member", lazy="raise")
