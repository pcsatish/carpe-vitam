"""Base extractor class and models."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


# Keyword prefix that anchors a date to a label in the report
_DATE_KEYWORD = (
    r"(?:report\s+date|sample\s+(?:collection\s+)?date|collection\s+date"
    r"|collected\s+on|reported\s+on|date\s+of\s+(?:report|collection)"
    r"|test\s+date|date)\s*[:\-]?\s*"
)

# Patterns tried in order: keyword-anchored first, then any date in text.
# Each tuple is (regex, list_of_strptime_formats).
_DATE_PATTERNS: list[tuple[str, list[str]]] = [
    # --- Keyword-anchored (more reliable) ---
    (_DATE_KEYWORD + r"(\d{1,2}/\d{1,2}/\d{4})", ["%d/%m/%Y"]),
    (_DATE_KEYWORD + r"(\d{1,2}-\d{1,2}-\d{4})", ["%d-%m-%Y"]),
    (_DATE_KEYWORD + r"(\d{1,2}[\s\-]\w{3,9},?\s*\d{4})", ["%d %b %Y", "%d-%b-%Y", "%d %B %Y", "%d-%B-%Y"]),
    (_DATE_KEYWORD + r"(\d{4}-\d{2}-\d{2})", ["%Y-%m-%d"]),
    (_DATE_KEYWORD + r"(\d{1,2}\.\d{1,2}\.\d{4})", ["%d.%m.%Y"]),
    # --- Fallback: first matching date anywhere in text ---
    (r"\b(\d{2}/\d{2}/\d{4})\b", ["%d/%m/%Y"]),
    (r"\b(\d{2}-\d{2}-\d{4})\b", ["%d-%m-%Y"]),
    (r"\b(\d{1,2}\s+\w{3,9},?\s*\d{4})\b", ["%d %b %Y", "%d %B %Y"]),
    (r"\b(\d{4}-\d{2}-\d{2})\b", ["%Y-%m-%d"]),
    (r"\b(\d{2}\.\d{2}\.\d{4})\b", ["%d.%m.%Y"]),
]


def extract_report_date(text: str) -> Optional[date]:
    """Extract a report date from text.

    Tries keyword-anchored patterns first (e.g. "Report Date: 22/03/2026"),
    then falls back to the first date found anywhere in the text.
    """
    for pattern, fmts in _DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        raw = match.group(1).replace(",", "").strip()
        for fmt in fmts:
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
    return None


@dataclass
class ExtractedTestResult:
    """A single extracted test result."""

    raw_name: str
    raw_value: Optional[float]
    raw_unit: str
    # Canonical values set after normalization
    canonical_name: Optional[str] = None
    analyte_id: Optional[str] = None
    canonical_value: Optional[float] = None
    canonical_unit: Optional[str] = None


@dataclass
class ExtractorOutput:
    """Output from an extractor."""

    patient_name: Optional[str]
    report_date: Optional[date]
    lab_name: Optional[str]
    tests: list[ExtractedTestResult]
    extraction_notes: str = ""
    success: bool = True


class BaseExtractor(ABC):
    """Base class for PDF extractors."""

    name: str = "BaseExtractor"
    priority: int = 999  # Lower = tried first

    @classmethod
    @abstractmethod
    def can_handle(cls, file_path: str, text_sample: str) -> bool:
        """
        Determine if this extractor can handle the given PDF.

        Args:
            file_path: Path to the PDF file
            text_sample: First 1000 chars of extracted text

        Returns:
            True if this extractor can handle the file
        """
        pass

    @abstractmethod
    async def extract(self, file_path: str) -> ExtractorOutput:
        """
        Extract test results from the PDF.

        Args:
            file_path: Path to the PDF file

        Returns:
            ExtractorOutput with extracted data
        """
        pass
