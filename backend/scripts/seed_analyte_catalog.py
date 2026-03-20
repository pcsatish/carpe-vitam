"""Seed the analyte catalog from legacy data files."""

import asyncio
import json
import sys
import os
from pathlib import Path
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from app.database import AsyncSessionLocal, Base, engine
from app.models.analyte import AnalyteCatalog, AnalyteAlias
from app.extraction.canonicalizer import Canonicalizer


async def seed_analyte_catalog():
    """Seed the analyte catalog from JSON files."""
    # Load canonical map (normalized_name -> [canonical_name, category])
    legacy_dir = Path(__file__).parent.parent.parent / "med_reports"
    canonical_map_path = legacy_dir / "normalization_map.json"
    unique_analytes_path = legacy_dir / "unique_analytes.json"

    if not canonical_map_path.exists():
        print(f"Error: {canonical_map_path} not found")
        return

    with open(canonical_map_path) as f:
        canonical_map = json.load(f)

    # Load unique analytes (all raw names encountered)
    unique_analytes = []
    if unique_analytes_path.exists():
        with open(unique_analytes_path) as f:
            unique_analytes = json.load(f)
    else:
        print(f"Warning: {unique_analytes_path} not found - will only use canonical_map")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed analyte_catalog and aliases
    async with AsyncSessionLocal() as db:
        # First, create all canonical entries from canonical_map
        for normalized_name, (canonical_name, category) in canonical_map.items():
            # Check if already exists
            result = await db.execute(
                select(AnalyteCatalog).where(
                    AnalyteCatalog.canonical_name == canonical_name
                )
            )
            analyte = result.scalar_one_or_none()

            if not analyte:
                analyte = AnalyteCatalog(
                    id=str(uuid.uuid4()),
                    canonical_name=canonical_name,
                    category=category,
                    canonical_unit="unknown",  # Will be refined later
                    description=None,
                    is_active=True,
                )
                db.add(analyte)

            # Create alias for the normalized name
            alias = AnalyteAlias(
                id=str(uuid.uuid4()),
                analyte_id=analyte.id,
                raw_name=normalized_name,
                lab_source=None,
            )
            db.add(alias)

        # Now process unique_analytes and create aliases
        for raw_analyte_name in unique_analytes:
            # Normalize the name
            normalized = Canonicalizer.normalize_name(raw_analyte_name)

            # Check if we already have a canonical mapping for this
            found = False
            for canonical_key, (canonical_name, category) in canonical_map.items():
                if canonical_key == normalized:
                    # Already handled above
                    found = True
                    break

            if not found:
                # Try to find a canonical entry that matches
                # For now, create as uncategorized
                result = await db.execute(
                    select(AnalyteCatalog).where(
                        AnalyteCatalog.canonical_name == normalized
                    )
                )
                analyte = result.scalar_one_or_none()

                if not analyte:
                    # Create new analyte for this variation
                    analyte = AnalyteCatalog(
                        id=str(uuid.uuid4()),
                        canonical_name=normalized,
                        category="Uncategorized",
                        canonical_unit="unknown",
                        description=None,
                        is_active=True,
                    )
                    db.add(analyte)

            # Create alias for the raw name
            result = await db.execute(
                select(AnalyteAlias).where(
                    AnalyteAlias.raw_name == normalized
                )
            )
            existing_alias = result.scalar_one_or_none()

            if not existing_alias:
                alias = AnalyteAlias(
                    id=str(uuid.uuid4()),
                    analyte_id=analyte.id,
                    raw_name=normalized,
                    lab_source=None,
                )
                db.add(alias)

        await db.commit()
        print(f"Seeded {len(canonical_map)} canonical analytes and {len(unique_analytes)} aliases")


if __name__ == "__main__":
    asyncio.run(seed_analyte_catalog())
