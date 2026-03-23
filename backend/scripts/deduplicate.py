"""
Idempotent deduplication script for lab_reports and test_results.

Run from the backend/ directory with the venv active:
    python -m scripts.deduplicate

What it does:
1. Deduplicates test_results: same (family_member_id, analyte_id, report_date, canonical_value)
   → keeps the oldest row, hard-deletes the rest.
2. Backfills file_hash on lab_reports from disk (where the file still exists).
3. Deduplicates lab_reports by file_hash + family_member_id
   → keeps the oldest non-deleted report, soft-deletes the rest (cascades test_results via is_deleted logic).

Safe to run multiple times — each step is a no-op if already clean.
"""

import asyncio
import hashlib
import os
import sys
from sqlalchemy import delete, select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.lab_report import LabReport
from app.models.test_result import TestResult


async def dedup_test_results(session) -> int:
    """
    Remove duplicate test_results rows.
    Duplicate = same (family_member_id, analyte_id, report_date, canonical_value).
    Keeps the row with the lowest created_at; hard-deletes the rest.
    Returns number of rows deleted.
    """
    result = await session.execute(select(TestResult).order_by(TestResult.created_at))
    rows = result.scalars().all()

    seen: dict[tuple, str] = {}  # key → id to keep
    to_delete: list[str] = []

    for row in rows:
        key = (row.family_member_id, row.analyte_id, str(row.report_date), str(row.canonical_value))
        if key in seen:
            to_delete.append(row.id)
        else:
            seen[key] = row.id

    if to_delete:
        await session.execute(delete(TestResult).where(TestResult.id.in_(to_delete)))
        await session.commit()

    return len(to_delete)


async def backfill_file_hashes(session) -> int:
    """
    Compute and store SHA-256 for lab_reports where file_hash is NULL and file exists on disk.
    Returns number of reports updated.
    """
    result = await session.execute(
        select(LabReport).where(LabReport.file_hash == None)  # noqa: E711
    )
    reports = result.scalars().all()

    updated = 0
    for report in reports:
        if report.storage_path and os.path.exists(report.storage_path):
            with open(report.storage_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            report.file_hash = file_hash
            updated += 1

    if updated:
        await session.commit()

    return updated


async def dedup_lab_reports(session) -> int:
    """
    Soft-delete duplicate lab_reports sharing the same (file_hash, family_member_id).
    Keeps the oldest non-deleted report; soft-deletes (is_deleted=True) the rest.
    Returns number of reports soft-deleted.
    """
    result = await session.execute(
        select(LabReport)
        .where(LabReport.file_hash != None, LabReport.is_deleted.is_(False))  # noqa: E711
        .order_by(LabReport.created_at)
    )
    reports = result.scalars().all()

    seen: dict[tuple, str] = {}  # (hash, member_id) → id to keep
    to_delete: list[LabReport] = []

    for report in reports:
        key = (report.file_hash, report.family_member_id)
        if key in seen:
            to_delete.append(report)
        else:
            seen[key] = report.id

    for report in to_delete:
        report.is_deleted = True

    if to_delete:
        await session.commit()

    return len(to_delete)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        print("=== Carpe Vitam deduplication ===")

        print("Deduplicating test_results...", end=" ", flush=True)
        n = await dedup_test_results(session)
        print(f"{n} rows deleted")

        print("Backfilling file hashes on lab_reports...", end=" ", flush=True)
        n = await backfill_file_hashes(session)
        print(f"{n} reports updated")

        print("Deduplicating lab_reports...", end=" ", flush=True)
        n = await dedup_lab_reports(session)
        print(f"{n} reports soft-deleted")

        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
