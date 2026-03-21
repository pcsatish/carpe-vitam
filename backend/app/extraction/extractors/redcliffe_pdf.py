"""Redcliffe Labs PDF extractor."""

import re
from datetime import date, datetime
from typing import Optional
import pdfplumber

from ..base import BaseExtractor, ExtractorOutput, ExtractedTestResult
from ..registry import ExtractorRegistry


@ExtractorRegistry.register
class RedcliffePDFExtractor(BaseExtractor):
    """Extractor for Redcliffe Labs reports.

    Redcliffe column layout: Test Name | Value | Unit | Reference Range | Status
    """

    name = "RedcliffePDFExtractor"
    priority = 200  # Higher than generic, lower than Thyrocare

    _IDENTIFIERS = ["REDCLIFFE", "REDCLIFFE LABS", "REDCLIFFE LIFETECH"]

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
                    lab_name="Redcliffe",
                    tests=tests,
                    extraction_notes=f"Redcliffe extractor: {len(tests)} tests",
                    success=len(tests) > 0,
                )
        except Exception as e:
            return ExtractorOutput(
                patient_name=None,
                report_date=None,
                lab_name="Redcliffe",
                tests=[],
                extraction_notes=f"Extraction failed: {e}",
                success=False,
            )

    def _extract_patient_name(self, text: str) -> Optional[str]:
        for pattern in [
            r"Patient\s*Name\s*[:\-]\s*(.+)",
            r"Name\s*[:\-]\s*(.*?)\(",
            r"Name\s*[:\-]\s*(.+)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_date(self, text: str) -> Optional[date]:
        for pattern, fmts in [
            (r"\d{2}/\d{2}/\d{4}", ["%d/%m/%Y"]),
            (r"\d{2}-\d{2}-\d{4}", ["%d-%m-%Y"]),
            (r"\d{2} \w{3},? \d{4}", ["%d %b %Y", "%d %B %Y"]),
        ]:
            match = re.search(pattern, text)
            if not match:
                continue
            raw = match.group(0).replace(",", "")
            for fmt in fmts:
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
        return None

    async def _extract_from_tables(self, pdf) -> list[ExtractedTestResult]:
        """Redcliffe tables: [Test Name, Value, Unit, Ref Range, Status]."""
        tests = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue
            for table in tables:
                if not table or len(table) < 2:
                    continue
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    raw_name = row[0]
                    raw_value = row[1]
                    raw_unit = row[2] if len(row) > 2 else ""

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
