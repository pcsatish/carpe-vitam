"""Base extractor class and models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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
    report_date: Optional[str]
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
