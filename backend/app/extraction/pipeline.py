"""Extraction pipeline orchestrator."""

import os
from pathlib import Path
from .registry import ExtractorRegistry
from .base import ExtractorOutput


class ExtractionPipeline:
    """Orchestrates the extraction process."""

    def __init__(self):
        """Initialize the pipeline."""
        # Import extractors to register them
        from .extractors import generic_pdf  # noqa

    async def extract(self, file_path: str) -> ExtractorOutput:
        """
        Extract test results from a file.

        Steps:
        1. Sample first 1000 chars of PDF text
        2. Find appropriate extractor
        3. Run extraction
        4. Return results
        """
        if not os.path.exists(file_path):
            return ExtractorOutput(
                patient_name=None,
                report_date=None,
                lab_name=None,
                tests=[],
                extraction_notes="File not found",
                success=False,
            )

        # Get text sample for extractor selection
        text_sample = self._get_text_sample(file_path)

        # Find extractor
        extractor_class = ExtractorRegistry.get_extractor(file_path, text_sample)
        if not extractor_class:
            return ExtractorOutput(
                patient_name=None,
                report_date=None,
                lab_name=None,
                tests=[],
                extraction_notes="No suitable extractor found",
                success=False,
            )

        # Run extraction
        extractor = extractor_class()
        output = await extractor.extract(file_path)

        return output

    def _get_text_sample(self, file_path: str) -> str:
        """Get first 1000 chars of text from PDF."""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                if pdf.pages:
                    text = pdf.pages[0].extract_text()
                    if text:
                        return text[:1000]
        except Exception:
            pass
        return ""
