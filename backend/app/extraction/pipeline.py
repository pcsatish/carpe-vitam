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
        from . import extractors  # noqa: F401

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
        """Get text sampled from the first 5 and last 2 pages of the PDF.

        Some labs (e.g. Thyrocare) put their branding only on the final summary
        page, so sampling only from the front misses the identifier. The front
        and tail are each limited independently so the tail is never truncated away.
        """
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages = pdf.pages
                n = len(pages)
                front_idx = list(range(min(5, n)))
                tail_idx = [i for i in range(max(0, n - 2), n) if i not in front_idx]
                front = "\n".join(pages[i].extract_text() or "" for i in front_idx)[:2000]
                tail = "\n".join(pages[i].extract_text() or "" for i in tail_idx)[:1000]
                return f"{front}\n{tail}".strip()
        except Exception:
            pass
        return ""
