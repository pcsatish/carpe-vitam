"""
Re-run extraction for lab_reports where lab_name is NULL.

Deletes existing test_results for each report first to avoid duplicates,
then re-runs the full extraction pipeline.

Run from the backend/ directory with the venv active:
    python -m scripts.reextract_missing_lab_names

Safe to run multiple times — skips reports whose lab_name is already set.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select

from app.database import AsyncSessionLocal
from app.models.lab_report import LabReport
from app.models.test_result import TestResult
from app.services.result_service import ResultService

UPLOADS_BASE = "/app/uploads"


async def main() -> None:
    service = ResultService()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LabReport).where(
                LabReport.lab_name.is_(None),
                LabReport.is_deleted.is_(False),
                LabReport.storage_path.is_not(None),
            )
        )
        reports = result.scalars().all()
        print(f"Found {len(reports)} reports with missing lab_name")

        for report in reports:
            full_path = os.path.join("/app", report.storage_path)
            if not os.path.exists(full_path):
                print(f"  SKIP {report.original_filename} — file not found at {full_path}")
                continue

            # Delete existing test_results for this report before re-extracting
            deleted = await session.execute(
                delete(TestResult).where(TestResult.lab_report_id == report.id)
            )
            await session.commit()

            print(
                f"  Re-extracting {report.original_filename}"
                f" (cleared {deleted.rowcount} existing results)..."
            )
            updated = await service.extract_and_persist(session, report.id, full_path)
            print(f"    → lab_name={updated.lab_name!r}, status={updated.extraction_status}")

        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
