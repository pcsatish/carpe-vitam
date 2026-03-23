"""Thyrocare PDF extractor."""

import re
from typing import Optional
import pdfplumber

from ..base import BaseExtractor, ExtractorOutput, ExtractedTestResult, extract_report_date
from ..registry import ExtractorRegistry


@ExtractorRegistry.register
class ThyrocarePDFExtractor(BaseExtractor):
    """Extractor for Thyrocare lab reports.

    Thyrocare column layout: Test Name | Method | Value | Unit | Bio. Ref. Interval
    Some sections (CBC, certain panels) render as 1-column tables where the
    entire row is packed into one cell: "NAME VALUE UNIT REFRANGE"
    """

    name = "ThyrocarePDFExtractor"
    priority = 100  # Higher priority than generic

    # Thyrocare-specific identifiers found in report headers
    _IDENTIFIERS = ["THYROCARE", "AAROGYAM", "THYRO CARE"]

    # Matches the first standalone number in a 1-column cell (the test value).
    # (?<=\s) prevents matching numbers embedded in names like "B-12" or "25-OH".
    _SINGLE_COL_VALUE_RE = re.compile(r"(?<=\s)([\d]+\.?[\d]*)(?=\s|$)")

    # Splits unit from ref range. Ref range patterns: "30-100", "0.02 - 0.5", "< 100", "> 5.38"
    _SINGLE_COL_UNIT_RE = re.compile(
        r"^(.+?)(?:\s+(?:[\d.]+\s*[-\u2013]\s*[\d.]+|[<>]\s*[\d.]+).*)?$"
    )

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
                report_date = extract_report_date(full_text)
                tests = await self._extract_from_tables(pdf)

                # Always supplement with regex — catches analytes the table
                # parser misses (e.g. units not handled by single-col parser).
                # Deduplicate by raw_name; table parser takes precedence.
                regex_tests = self._extract_from_regex(full_text)
                table_names = {t.raw_name.upper() for t in tests}
                for t in regex_tests:
                    if t.raw_name.upper() not in table_names:
                        tests.append(t)

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
                    if not row:
                        continue
                    if len(row) >= 4:
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

                        tests.append(
                            ExtractedTestResult(
                                raw_name=str(raw_name).strip(),
                                raw_value=value,
                                raw_unit=str(raw_unit).strip() if raw_unit else "",
                            )
                        )
                    elif len(row) == 1 and row[0]:
                        # Some panels (CBC, certain hormone tests) render as 1-column
                        # tables with format: "NAME VALUE UNIT REFRANGE" in one cell.
                        result = self._parse_single_col_row(str(row[0]))
                        if result:
                            tests.append(result)
        return tests

    def _parse_single_col_row(self, cell: str) -> Optional[ExtractedTestResult]:
        """Parse a 1-column cell of the form: NAME VALUE UNIT REFRANGE."""
        cell = cell.strip()
        # Skip section headers, footnotes, address lines, and patient detail rows
        if not cell or "Ready" in cell or ":" in cell or "\n" in cell:
            return None

        m = self._SINGLE_COL_VALUE_RE.search(cell)
        if not m:
            return None

        name = cell[: m.start()].strip()
        value_str = m.group(1)
        rest = cell[m.end() :].strip()

        if not name or name.endswith(",") or name.endswith("-"):
            return None

        unit = ""
        if rest:
            unit_m = self._SINGLE_COL_UNIT_RE.match(rest)
            unit = unit_m.group(1).strip() if unit_m else rest.split()[0]

        # Unit sanity check: must be present and look like a real unit
        if not unit or not (unit[0].isalpha() or unit[0] == "%"):
            return None
        if len(unit) > 20 or "," in unit:
            return None

        try:
            return ExtractedTestResult(
                raw_name=name,
                raw_value=float(value_str),
                raw_unit=unit,
            )
        except ValueError:
            return None

    def _extract_from_regex(self, text: str) -> list[ExtractedTestResult]:
        tests = []
        for line in text.split("\n"):
            result = self._parse_single_col_row(line)
            if result:
                tests.append(result)
        return tests
