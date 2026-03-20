"""Test name canonicalization - normalize raw names and map to canonical analytes."""

import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.analyte import AnalyteAlias, AnalyteCatalog


class Canonicalizer:
    """Handles normalization and lookup of test names."""

    # Method suffixes to strip
    METHOD_SUFFIXES = [
        "PHOTOMETRY",
        "IMMUNOTURBIDIMETRY",
        "IMMUNOTURBIDIMETR",
        "ISE",
        "INDIRECT",
        "CALCULATED",
        "ECLIA",
        "CMIA",
        "CLIA",
    ]

    @classmethod
    def normalize_name(cls, raw_name: str) -> str:
        """
        Normalize a raw test name for canonical lookup.

        Steps:
        1. Uppercase
        2. Strip punctuation -> spaces
        3. Collapse whitespace
        4. Strip method suffixes
        5. Collapse spaced abbreviations (e.g., "C M I A" -> "CMIA")
        """
        name = str(raw_name).upper().strip()

        # Replace punctuation with spaces
        name = re.sub(r"[^\w\s]", " ", name)

        # Collapse whitespace
        name = re.sub(r"\s+", " ", name).strip()

        # Strip method suffixes
        for suffix in cls.METHOD_SUFFIXES:
            if name.endswith(" " + suffix):
                name = name[:-len(suffix)-1].strip()
            elif name.endswith(suffix) and name != suffix:
                name = name[:-len(suffix)].strip()

        # Collapse spaced abbreviations: "C M I A" -> "CMIA", "E C L I A" -> "ECLIA"
        # Only collapse consecutive single-character tokens (pdfplumber artifact fix)
        tokens = name.split()
        result = []
        i = 0
        while i < len(tokens):
            if len(tokens[i]) == 1:
                j = i
                while j < len(tokens) and len(tokens[j]) == 1:
                    j += 1
                result.append("".join(tokens[i:j]))
                i = j
            else:
                result.append(tokens[i])
                i += 1
        name = " ".join(result)

        return name.strip()

    @classmethod
    async def lookup_canonical(
        cls,
        db: AsyncSession,
        raw_name: str,
        lab_source: str | None = None,
    ) -> tuple[str | None, str | None]:
        """
        Lookup canonical name and analyte ID for a raw test name.

        Returns:
            (canonical_name, analyte_id) or (None, None) if not found
        """
        normalized = cls.normalize_name(raw_name)

        # First try: exact match in aliases (with or without lab_source)
        if lab_source:
            result = await db.execute(
                select(AnalyteAlias).where(
                    (AnalyteAlias.raw_name == normalized) &
                    (AnalyteAlias.lab_source == lab_source)
                )
            )
            alias = result.scalar_one_or_none()
            if alias:
                analyte = await db.get(AnalyteCatalog, alias.analyte_id)
                if analyte:
                    return analyte.canonical_name, analyte.id

        # Second try: exact match without lab_source filter
        result = await db.execute(
            select(AnalyteAlias).where(AnalyteAlias.raw_name == normalized)
        )
        alias = result.scalar_one_or_none()
        if alias:
            analyte = await db.get(AnalyteCatalog, alias.analyte_id)
            if analyte:
                return analyte.canonical_name, analyte.id

        # Not found
        return None, None
