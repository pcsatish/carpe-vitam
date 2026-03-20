"""Service for extracting and persisting test results."""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.lab_report import LabReport, ExtractionStatus
from ..models.test_result import TestResult
from ..extraction.pipeline import ExtractionPipeline
from ..extraction.canonicalizer import Canonicalizer
from ..extraction.unit_converter import UnitConverter


class ResultService:
    """Service for extracting test results from lab reports."""

    def __init__(self):
        """Initialize the service."""
        self.pipeline = ExtractionPipeline()

    async def extract_and_persist(
        self,
        db: AsyncSession,
        lab_report_id: str,
        file_path: str,
    ) -> LabReport:
        """
        Extract test results from a PDF and persist to database.

        Args:
            db: Database session
            lab_report_id: ID of the lab report
            file_path: Path to the PDF file

        Returns:
            Updated LabReport with extraction status
        """
        lab_report = await db.get(LabReport, lab_report_id)
        if not lab_report:
            raise ValueError(f"Lab report {lab_report_id} not found")

        # Update status to processing
        lab_report.extraction_status = ExtractionStatus.PROCESSING
        lab_report.updated_at = datetime.utcnow()
        await db.commit()

        try:
            # Run extraction pipeline
            extractor_output = await self.pipeline.extract(file_path)

            # Update lab report with extracted metadata
            if extractor_output.patient_name:
                lab_report.raw_patient_name = extractor_output.patient_name
            if extractor_output.lab_name:
                lab_report.lab_name = extractor_output.lab_name
            if extractor_output.report_date:
                lab_report.report_date = extractor_output.report_date
            lab_report.extractor_used = extractor_output.lab_name or "Unknown"
            lab_report.extraction_notes = extractor_output.extraction_notes

            # Canonicalize and persist test results
            test_results = []
            for extracted_test in extractor_output.tests:
                # Lookup canonical name and analyte ID
                canonical_name, analyte_id = await Canonicalizer.lookup_canonical(
                    db,
                    extracted_test.raw_name,
                    lab_source=lab_report.lab_name,
                )

                if not canonical_name or not analyte_id:
                    # Skip unmapped analytes for now
                    # In Phase 3, we'll queue these for manual review
                    continue

                # Convert units
                canonical_value, canonical_unit = UnitConverter.convert(
                    extracted_test.raw_value,
                    extracted_test.raw_unit,
                    canonical_name,
                )

                # Create test result
                test_result = TestResult(
                    id=str(uuid.uuid4()),
                    lab_report_id=lab_report_id,
                    family_member_id=lab_report.family_member_id,
                    analyte_id=analyte_id,
                    report_date=lab_report.report_date,
                    raw_name=extracted_test.raw_name,
                    raw_value=extracted_test.raw_value,
                    raw_unit=extracted_test.raw_unit,
                    canonical_value=canonical_value,
                    canonical_unit=canonical_unit,
                    is_canonical=canonical_name is not None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                # Check if out of range (simplified - no reference ranges yet)
                test_result.is_out_of_range = False

                db.add(test_result)
                test_results.append(test_result)

            # Update lab report status
            if test_results:
                lab_report.extraction_status = ExtractionStatus.SUCCESS
            else:
                lab_report.extraction_status = ExtractionStatus.FAILED
                lab_report.extraction_notes = "No test results could be extracted"

            lab_report.updated_at = datetime.utcnow()
            await db.commit()

        except Exception as e:
            lab_report.extraction_status = ExtractionStatus.FAILED
            lab_report.extraction_notes = f"Extraction error: {str(e)}"
            lab_report.updated_at = datetime.utcnow()
            await db.commit()

        await db.refresh(lab_report)
        return lab_report
