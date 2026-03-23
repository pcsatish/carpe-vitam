"""Service for handling PDF uploads."""

import hashlib
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.family import FamilyMember
from ..models.lab_report import ExtractionStatus, LabReport


class DuplicateUploadError(ValueError):
    """Raised when a duplicate PDF is uploaded for the same family member."""


class UploadService:
    """Service for handling lab report uploads."""

    UPLOAD_DIR = Path("uploads")

    def __init__(self):
        """Initialize the upload service."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def receive_upload(
        self,
        db: AsyncSession,
        file_content: bytes,
        filename: str,
        family_member_id: str,
        uploaded_by_user_id: str,
        report_date: Optional[date] = None,
    ) -> LabReport:
        """
        Receive and store an uploaded PDF.

        Args:
            db: Database session
            file_content: Raw file bytes
            filename: Original filename
            family_member_id: ID of family member this report is for
            uploaded_by_user_id: ID of user who uploaded

        Returns:
            LabReport object
        """
        # Verify family member exists
        family_member = await db.get(FamilyMember, family_member_id)
        if not family_member:
            raise ValueError(f"Family member {family_member_id} not found")

        # Compute SHA-256 hash and reject duplicate uploads
        file_hash = hashlib.sha256(file_content).hexdigest()
        existing = await db.execute(
            select(LabReport).where(
                LabReport.file_hash == file_hash,
                LabReport.family_member_id == family_member_id,
                LabReport.is_deleted.is_(False),
            )
        )
        if existing.scalars().first():
            raise DuplicateUploadError("This file has already been uploaded for this family member")

        # Generate storage path
        report_id = str(uuid.uuid4())
        storage_path = str(self.UPLOAD_DIR / f"{report_id}_{filename}")

        # Write file to disk
        with open(storage_path, "wb") as f:
            f.write(file_content)

        # Create lab report record
        lab_report = LabReport(
            file_hash=file_hash,
            id=report_id,
            family_member_id=family_member_id,
            uploaded_by_user_id=uploaded_by_user_id,
            original_filename=filename,
            storage_path=storage_path,
            report_date=report_date,  # user-provided fallback; overwritten if extractor finds a date
            extraction_status=ExtractionStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(lab_report)
        await db.commit()
        await db.refresh(lab_report)

        return lab_report

    async def delete_upload(self, db: AsyncSession, lab_report_id: str) -> bool:
        """
        Delete an uploaded PDF and mark report as deleted.

        Args:
            db: Database session
            lab_report_id: ID of lab report to delete

        Returns:
            True if successful
        """
        lab_report = await db.get(LabReport, lab_report_id)
        if not lab_report:
            return False

        # Delete file from disk if it exists
        if lab_report.storage_path and os.path.exists(lab_report.storage_path):
            try:
                os.remove(lab_report.storage_path)
            except OSError:
                pass

        # Mark as deleted (soft delete)
        lab_report.is_deleted = True
        lab_report.updated_at = datetime.utcnow()
        await db.commit()

        return True
