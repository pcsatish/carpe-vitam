"""Thyrocare PDF extractor."""

import re
from datetime import date
from typing import Optional
import pdfplumber

from ..base import BaseExtractor, ExtractorOutput, ExtractedTestResult
from ..registry import ExtractorRegistry


@ExtractorRegistry.register
class ThyrocarePDFExtractor(BaseExtractor):
    """Extractor for Thyrocare lab reports.

    Thyrocare column layout: Test Name | Method | Value | Unit | Bio. Ref. Interval
    """

    name = "ThyrocarePDFExtractor"
    priority = 100  # Higher priority than generic

    # Thyrocare-specific identifiers found in report headers
    _IDENTIFIERS = ["THYROCARE", "AAROGYAM", "THYRO CARE"]

    @classmethod
    def can_handle(cls, file_path: str, text_sample: str) -> bool:
        upper = text_sample.upper()
        return any(ident in upper for ident in cls._IDENTIFIERS)

    async def extract(self, file_path: str) -> ExtractorOutput:
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

                patient_name = self._extract_patient_name(full_text)
                report_date = self._extract_date(full_text)
                tests = await self._extract_from_tables(pdf)

                if not tests:
                    tests = self._extract_from_regex(full_text)

                return ExtractorOutput(
                    patient_name=patient_name,
                    report_date=report_date,
                    lab_name="Thyrocare",
                    tests=tests,
                    extraction_notes=f"Thyrocare extractor: {len(tests)} tests",
                    success=len(tests) > 0,
                )
        except Exception as e:
            return ExtractorOutput(
                patient_name=None,
                report_date=None,
                lab_name="Thyrocare",
                tests=[],
                extraction_notes=f"Extraction failed: {e}",
                success=False,
            )

    def _extract_patient_name(self, text: str) -> Optional[str]:
        for pattern in [
            r"Name\s*:\s*(.*?)\(",
            r"Patient\s*Name\s*:\s*(.+)",
            r"Name\s*:\s*(.+)",
        ]:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_date(self, text: str) -> Optional[date]:
        from datetime import datetime
        # Thyrocare uses "DD Mon YYYY", "DD Mon, YYYY", or "DD/MM/YYYY"
        for pattern, fmt in [
            (r"\d{2} \w{3},? \d{4}", None),
            (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),
        ]:
            match = re.search(pattern, text)
            if not match:
                continue
            raw = match.group(0).replace(",", "")
            if fmt:
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
            for f in ("%d %b %Y", "%d %B %Y"):
                try:
                    return datetime.strptime(raw, f).date()
                except ValueError:
                    continue
        return None

    async def _extract_from_tables(self, pdf) -> list[ExtractedTestResult]:
        """Thyrocare tables: [Test Name, Method, Value, Unit, Ref Range]."""
        tests = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue
            for table in tables:
                if not table or len(table) < 2:
                    continue
                for row in table:
                    if not row or len(row) < 4:
                        continue
                    raw_name = row[0]
                    # col 1 = method, col 2 = value, col 3 = unit
                    raw_value = row[2]
                    raw_unit = row[3] if len(row) > 3 else ""

                    if not raw_name:
                        continue

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
        tests = []
        pattern = r"^(.*?)\s+([-+]?\d*\.?\d+)\s+(mg/dL|U/L|g/dL|ng/dL|µg/dL|µIU/mL|mmol/L|mEq/L|IU/L|pg/mL)"
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
