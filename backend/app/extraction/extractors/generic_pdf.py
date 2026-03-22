"""Generic PDF extractor - works with various lab report formats."""

import re
from typing import Optional
import pdfplumber

from ..base import BaseExtractor, ExtractorOutput, ExtractedTestResult, extract_report_date
from ..registry import ExtractorRegistry


@ExtractorRegistry.register
class GenericPDFExtractor(BaseExtractor):
    """Generic PDF extractor with table-first fallback to regex."""

    name = "GenericPDFExtractor"
    priority = 999  # Lowest priority - used as fallback

    @classmethod
    def can_handle(cls, file_path: str, text_sample: str) -> bool:
        """Can handle any PDF (used as fallback)."""
        return file_path.lower().endswith('.pdf')

    async def extract(self, file_path: str) -> ExtractorOutput:
        """Extract test results from PDF."""
        tests = []

        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

                # Extract metadata
                patient_name = self._extract_patient_name(full_text)
                report_date = extract_report_date(full_text)

                # Try table extraction first
                tests = await self._extract_from_tables(pdf)

                if not tests:
                    # Fallback to regex extraction
                    tests = self._extract_from_regex(full_text)

                return ExtractorOutput(
                    patient_name=patient_name,
                    report_date=report_date,
                    lab_name=None,
                    tests=tests,
                    extraction_notes=f"Extracted {len(tests)} tests",
                    success=len(tests) > 0,
                )

        except Exception as e:
            return ExtractorOutput(
                patient_name=None,
                report_date=None,
                lab_name=None,
                tests=[],
                extraction_notes=f"Extraction failed: {str(e)}",
                success=False,
            )

    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text."""
        match = re.search(r"Name\s*:\s*(.*?)\(", text)
        if match:
            return match.group(1).strip()
        return None

    async def _extract_from_tables(self, pdf) -> list[ExtractedTestResult]:
        """Extract test results from PDF tables."""
        tests = []

        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Assume columns: [0] = name, [2] = value, [3] = unit
                for row in table:
                    if not row or len(row) < 4:
                        continue

                    raw_name = row[0]
                    raw_value = row[2]
                    raw_unit = row[3]

                    if not raw_name:
                        continue

                    # Try to parse value
                    try:
                        value = float(str(raw_value).strip())
                    except (ValueError, TypeError):
                        continue

                    tests.append(ExtractedTestResult(
                        raw_name=str(raw_name).strip(),
                        raw_value=value,
                        raw_unit=str(raw_unit).strip() if raw_unit else "",
                    ))

        return tests

    def _extract_from_regex(self, text: str) -> list[ExtractedTestResult]:
        """Extract test results using regex fallback."""
        tests = []

        # Pattern: TEST NAME   VALUE   UNIT
        pattern = r"^(.*?)\s+([-+]?\d*\.?\d+)\s+(mg/dL|U/L|gm/dL|ng/dL|µg/dL|µIU/mL|mmol/L|mL/min/1\.73 m2)"

        for line in text.split("\n"):
            match = re.match(pattern, line.strip())
            if not match:
                continue

            raw_name = match.group(1).strip()
            try:
                raw_value = float(match.group(2))
            except ValueError:
                continue
            raw_unit = match.group(3)

            tests.append(ExtractedTestResult(
                raw_name=raw_name,
                raw_value=raw_value,
                raw_unit=raw_unit,
            ))

        return tests
