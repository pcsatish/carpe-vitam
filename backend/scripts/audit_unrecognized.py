"""
Dry-run audit of unrecognized analytes across all uploaded PDFs.

Reads every lab report whose file still exists on disk, runs the extraction
pipeline, and reports which raw names failed catalog lookup — without writing
anything to the database.

Run from the backend/ directory:
    python -m scripts.audit_unrecognized

Output: grouped by lab source, sorted by frequency descending.
"""

import asyncio
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.extraction.canonicalizer import Canonicalizer
from app.extraction.pipeline import ExtractionPipeline
from app.models.lab_report import LabReport


async def main() -> None:
    pipeline = ExtractionPipeline()

    # missed[lab_source][normalized_raw_name] = count
    missed: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_reports = 0
    skipped_no_file = 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LabReport).where(LabReport.is_deleted.is_(False))
        )
        reports = result.scalars().all()

        for report in reports:
            if not report.storage_path or not os.path.exists(report.storage_path):
                skipped_no_file += 1
                continue

            total_reports += 1
            output = await pipeline.extract(report.storage_path)
            lab_source = output.lab_name or report.lab_name or "Unknown"

            for test in output.tests:
                canonical_name, analyte_id = await Canonicalizer.lookup_canonical(
                    db, test.raw_name, lab_source=lab_source
                )
                if not canonical_name:
                    normalized = Canonicalizer.normalize_name(test.raw_name)
                    missed[lab_source][normalized] += 1

    # Print report
    print(f"\n=== Unrecognized analyte audit ===")
    print(f"Reports scanned: {total_reports}  |  Skipped (no file on disk): {skipped_no_file}\n")

    if not missed:
        print("No unrecognized analytes found — catalog coverage is complete.")
        return

    total_missed = sum(sum(counts.values()) for counts in missed.values())
    print(f"Total unrecognized analyte occurrences: {total_missed}\n")

    for lab_source, counts in sorted(missed.items()):
        print(f"── {lab_source} ──")
        for name, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {count:>4}x  {name}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
