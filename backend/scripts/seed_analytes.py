#!/usr/bin/env python3
"""
Seed extended analyte catalog (~75 tests) with aliases and reference ranges.
Run from backend/: python -m scripts.seed_analytes
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/carpe_vitam",
)

# ---------------------------------------------------------------------------
# Catalog definition
# Each entry:
#   canonical_name, category, canonical_unit, aliases (list of raw names after normalization),
#   ref_ranges: list of (low_normal, high_normal, sex, age_min, age_max, unit)
# ---------------------------------------------------------------------------

ANALYTES = [
    # ── Lipid ──────────────────────────────────────────────────────────────
    {
        "canonical_name": "Total Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "TOTAL CHOLESTEROL",
            "TOTAL CHOLESTEROL PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0, "high": 200, "sex": None},
        ],
    },
    {
        "canonical_name": "HDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "HDL CHOLESTEROL DIRECT",
            "HDL CHOLESTEROL DIRECT PHOTOMETRY",
            "HDL CHOLESTEROL",
        ],
        "ref_ranges": [
            {"low": 40, "high": 60, "sex": "M"},
            {"low": 50, "high": 80, "sex": "F"},
        ],
    },
    {
        "canonical_name": "LDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "LDL CHOLESTEROL DIRECT",
            "LDL CHOLESTEROL DIRECT PHOTOMETRY",
            "LDL CHOLESTEROL",
        ],
        "ref_ranges": [
            {"low": 0, "high": 100, "sex": None},
        ],
    },
    {
        "canonical_name": "Triglycerides",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "TRIGLYCERIDES",
            "TRIGLYCERIDES PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0, "high": 150, "sex": None},
        ],
    },
    {
        "canonical_name": "VLDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "VLDL CHOLESTEROL",
            "VLDL CHOLESTEROL CALCULATED",
        ],
        "ref_ranges": [
            {"low": 2, "high": 30, "sex": None},
        ],
    },
    {
        "canonical_name": "Non-HDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "NON HDL CHOLESTEROL",
            "NON HDL CHOLESTEROL CALCULATED",
            "NON-HDL CHOLESTEROL",
        ],
        "ref_ranges": [
            {"low": 0, "high": 130, "sex": None},
        ],
    },
    {
        "canonical_name": "Apolipoprotein A1",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "APOLIPOPROTEIN A1 APO A1",
            "APOLIPOPROTEIN A1 APO A1 IMMUNOTURBIDIMETRY",
        ],
        "ref_ranges": [
            {"low": 94, "high": 178, "sex": "M"},
            {"low": 101, "high": 198, "sex": "F"},
        ],
    },
    {
        "canonical_name": "Apolipoprotein B",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "APOLIPOPROTEIN B APO B",
            "APOLIPOPROTEIN B APO B IMMUNOTURBIDIMETRY",
        ],
        "ref_ranges": [
            {"low": 55, "high": 140, "sex": "M"},
            {"low": 45, "high": 120, "sex": "F"},
        ],
    },
    {
        "canonical_name": "Lipoprotein A",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "LIPOPROTEIN A LP A",
            "LIPOPROTEIN A LP A IMMUNOTURBIDIMETRY",
        ],
        "ref_ranges": [
            {"low": 0, "high": 30, "sex": None},
        ],
    },
    # ── Liver ───────────────────────────────────────────────────────────────
    {
        "canonical_name": "Alkaline Phosphatase",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "ALKALINE PHOSPHATASE",
            "ALKALINE PHOSPHATASE PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 44, "high": 147, "sex": None},
        ],
    },
    {
        "canonical_name": "AST (SGOT)",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "ASPARTATE AMINOTRANSFERASE SGOT",
            "ASPARTATE AMINOTRANSFERASE SGOT PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 10, "high": 40, "sex": None},
        ],
    },
    {
        "canonical_name": "ALT (SGPT)",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "ALANINE TRANSAMINASE SGPT",
            "ALANINE TRANSAMINASE SGPT PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 7, "high": 56, "sex": None},
        ],
    },
    {
        "canonical_name": "GGT",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "GAMMA GLUTAMYL TRANSFERASE GGT",
            "GAMMA GLUTAMYL TRANSFERASE GGT PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 8, "high": 61, "sex": "M"},
            {"low": 5, "high": 36, "sex": "F"},
        ],
    },
    {
        "canonical_name": "Total Bilirubin",
        "category": "Liver",
        "canonical_unit": "mg/dL",
        "aliases": [
            "BILIRUBIN TOTAL",
            "BILIRUBIN TOTAL PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0.2, "high": 1.2, "sex": None},
        ],
    },
    {
        "canonical_name": "Direct Bilirubin",
        "category": "Liver",
        "canonical_unit": "mg/dL",
        "aliases": [
            "BILIRUBIN DIRECT",
            "BILIRUBIN DIRECT PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0.0, "high": 0.3, "sex": None},
        ],
    },
    {
        "canonical_name": "Indirect Bilirubin",
        "category": "Liver",
        "canonical_unit": "mg/dL",
        "aliases": [
            "BILIRUBIN INDIRECT",
            "BILIRUBIN INDIRECT CALCULATED",
        ],
        "ref_ranges": [
            {"low": 0.2, "high": 0.9, "sex": None},
        ],
    },
    {
        "canonical_name": "Albumin",
        "category": "Liver",
        "canonical_unit": "g/dL",
        "aliases": [
            "ALBUMIN SERUM",
            "ALBUMIN SERUM PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 3.5, "high": 5.0, "sex": None},
        ],
    },
    {
        "canonical_name": "Total Protein",
        "category": "Liver",
        "canonical_unit": "g/dL",
        "aliases": [
            "PROTEIN TOTAL",
            "PROTEIN TOTAL PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 6.3, "high": 8.2, "sex": None},
        ],
    },
    {
        "canonical_name": "Globulin",
        "category": "Liver",
        "canonical_unit": "g/dL",
        "aliases": [
            "SERUM GLOBULIN",
            "SERUM GLOBULIN CALCULATED",
            "SERUM GLOBULIN PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 2.0, "high": 3.5, "sex": None},
        ],
    },
    # ── Renal ───────────────────────────────────────────────────────────────
    {
        "canonical_name": "BUN",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "BLOOD UREA NITROGEN BUN",
            "BLOOD UREA NITROGEN BUN PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 7, "high": 20, "sex": None},
        ],
    },
    {
        "canonical_name": "Creatinine",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "CREATININE SERUM",
            "CREATININE SERUM PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0.74, "high": 1.35, "sex": "M"},
            {"low": 0.59, "high": 1.04, "sex": "F"},
        ],
    },
    {
        "canonical_name": "Calcium",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "CALCIUM",
            "CALCIUM PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 8.5, "high": 10.2, "sex": None},
        ],
    },
    {
        "canonical_name": "Uric Acid",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "URIC ACID",
            "URIC ACID PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 3.4, "high": 7.0, "sex": "M"},
            {"low": 2.4, "high": 6.0, "sex": "F"},
        ],
    },
    {
        "canonical_name": "Urea",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "UREA CALCULATED",
            "UREA CALCULATED CALCULATED",
        ],
        "ref_ranges": [
            {"low": 15, "high": 40, "sex": None},
        ],
    },
    {
        "canonical_name": "eGFR",
        "category": "Renal",
        "canonical_unit": "mL/min/1.73 m2",
        "aliases": [
            "EST GLOMERULAR FILTRATION RATE EGFR",
            "EST GLOMERULAR FILTRATION RATE EGFR CALCULATED",
        ],
        "ref_ranges": [
            {"low": 90, "high": None, "sex": None},
        ],
    },
    # ── Thyroid ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "T3",
        "category": "Thyroid",
        "canonical_unit": "ng/dL",
        "aliases": [
            "TOTAL TRIIODOTHYRONINE T3",
            "TOTAL TRIIODOTHYRONINE T3 CMIA",
            "TOTAL TRIIODOTHYRONINE T3 ECLIA",
        ],
        "ref_ranges": [
            {"low": 80, "high": 200, "sex": None},
        ],
    },
    {
        "canonical_name": "T4",
        "category": "Thyroid",
        "canonical_unit": "µg/dL",
        "aliases": [
            "TOTAL THYROXINE T4",
            "TOTAL THYROXINE T4 CMIA",
            "TOTAL THYROXINE T4 ECLIA",
        ],
        "ref_ranges": [
            {"low": 5.0, "high": 12.0, "sex": None},
        ],
    },
    {
        "canonical_name": "TSH",
        "category": "Thyroid",
        "canonical_unit": "µIU/mL",
        "aliases": [
            "TSH ULTRASENSITIVE",
            "TSH ULTRASENSITIVE CMIA",
            "TSH ULTRASENSITIVE ECLIA",
        ],
        "ref_ranges": [
            {"low": 0.27, "high": 4.2, "sex": None},
        ],
    },
    # ── Glucose ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Fasting Blood Sugar",
        "category": "Glucose",
        "canonical_unit": "mg/dL",
        "aliases": [
            "FASTING BLOOD SUGAR GLUCOSE",
            "FASTING BLOOD SUGAR GLUCOSE PHOTOMETRY",
            "FASTING BLOOD SUGAR",
            "FASTING BLOOD SUGAR PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 70, "high": 100, "sex": None},
        ],
    },
    {
        "canonical_name": "Average Blood Glucose",
        "category": "Glucose",
        "canonical_unit": "mg/dL",
        "aliases": [
            "AVERAGE BLOOD GLUCOSE ABG",
            "AVERAGE BLOOD GLUCOSE ABG CALCULATED",
        ],
        "ref_ranges": [
            {"low": 70, "high": 154, "sex": None},
        ],
    },
    # ── Electrolyte ─────────────────────────────────────────────────────────
    {
        "canonical_name": "Sodium",
        "category": "Electrolyte",
        "canonical_unit": "mEq/L",
        "aliases": [
            "SODIUM ISE",
            "SODIUM ISE INDIRECT",
        ],
        "ref_ranges": [
            {"low": 136, "high": 145, "sex": None},
        ],
    },
    {
        "canonical_name": "Chloride",
        "category": "Electrolyte",
        "canonical_unit": "mEq/L",
        "aliases": [
            "CHLORIDE",
            "CHLORIDE ISE",
            "CHLORIDE ISE INDIRECT",
        ],
        "ref_ranges": [
            {"low": 98, "high": 107, "sex": None},
        ],
    },
    {
        "canonical_name": "Magnesium",
        "category": "Electrolyte",
        "canonical_unit": "mg/dL",
        "aliases": [
            "MAGNESIUM",
            "MAGNESIUM PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 1.7, "high": 2.2, "sex": None},
        ],
    },
    # ── Hematology / Iron ────────────────────────────────────────────────────
    {
        "canonical_name": "Iron",
        "category": "Hematology",
        "canonical_unit": "µg/dL",
        "aliases": [
            "IRON",
            "IRON PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 65, "high": 175, "sex": "M"},
            {"low": 50, "high": 170, "sex": "F"},
        ],
    },
    {
        "canonical_name": "TIBC",
        "category": "Hematology",
        "canonical_unit": "µg/dL",
        "aliases": [
            "TOTAL IRON BINDING CAPACITY TIBC",
            "TOTAL IRON BINDING CAPACITY TIBC PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 250, "high": 370, "sex": None},
        ],
    },
    {
        "canonical_name": "UIBC",
        "category": "Hematology",
        "canonical_unit": "µg/dL",
        "aliases": [
            "UNSAT IRON BINDING CAPACITY UIBC",
            "UNSAT IRON BINDING CAPACITY UIBC PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 150, "high": 375, "sex": None},
        ],
    },
    # ── Minerals ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Serum Zinc",
        "category": "Minerals",
        "canonical_unit": "µg/dL",
        "aliases": [
            "SERUM ZINC",
            "SERUM ZINC PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 70, "high": 120, "sex": None},
        ],
    },
    {
        "canonical_name": "Serum Copper",
        "category": "Minerals",
        "canonical_unit": "µg/dL",
        "aliases": [
            "SERUM COPPER",
            "SERUM COPPER PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 70, "high": 140, "sex": None},
        ],
    },
    # ── Pancreas ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Amylase",
        "category": "Pancreas",
        "canonical_unit": "U/L",
        "aliases": [
            "AMYLASE",
            "AMYLASE PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 30, "high": 110, "sex": None},
        ],
    },
    {
        "canonical_name": "Lipase",
        "category": "Pancreas",
        "canonical_unit": "U/L",
        "aliases": [
            "LIPASE",
            "LIPASE PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0, "high": 160, "sex": None},
        ],
    },
    # ── Hormones ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Testosterone",
        "category": "Hormones",
        "canonical_unit": "ng/dL",
        "aliases": [
            "TESTOSTERONE",
            "TESTOSTERONE CLIA",
            "TESTOSTERONE ECLIA",
        ],
        "ref_ranges": [
            {"low": 264, "high": 916, "sex": "M"},
            {"low": 15, "high": 70, "sex": "F"},
        ],
    },
    # ── Cardiac ──────────────────────────────────────────────────────────────
    {
        "canonical_name": "Lp-PLA2",
        "category": "Cardiac",
        "canonical_unit": "nmol/min/mL",
        "aliases": [
            "LP PLA2",
            "LP PLA2 PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0, "high": 200, "sex": None},
        ],
    },
    # ── Metabolic ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Blood Ketone (D3HB)",
        "category": "Metabolic",
        "canonical_unit": "mmol/L",
        "aliases": [
            "BLOOD KETONE D3HB",
            "BLOOD KETONE D3HB PHOTOMETRY",
        ],
        "ref_ranges": [
            {"low": 0.0, "high": 0.6, "sex": None},
        ],
    },
]


async def seed(db: AsyncSession) -> None:
    import uuid
    from datetime import datetime

    inserted_analytes = 0
    inserted_aliases = 0
    inserted_ranges = 0

    for entry in ANALYTES:
        canonical_name = entry["canonical_name"]

        # Upsert analyte
        result = await db.execute(
            text("SELECT id FROM analyte_catalog WHERE canonical_name = :name"),
            {"name": canonical_name},
        )
        row = result.fetchone()

        if row:
            analyte_id = row[0]
        else:
            analyte_id = str(uuid.uuid4())
            await db.execute(
                text("""
                    INSERT INTO analyte_catalog (id, canonical_name, category, canonical_unit, is_active)
                    VALUES (:id, :name, :category, :unit, true)
                """),
                {
                    "id": analyte_id,
                    "name": canonical_name,
                    "category": entry["category"],
                    "unit": entry["canonical_unit"],
                },
            )
            inserted_analytes += 1

        # Upsert aliases
        for raw_name in entry.get("aliases", []):
            existing = await db.execute(
                text("SELECT id FROM analyte_aliases WHERE raw_name = :raw AND analyte_id = :aid"),
                {"raw": raw_name, "aid": analyte_id},
            )
            if not existing.fetchone():
                await db.execute(
                    text("""
                        INSERT INTO analyte_aliases (id, analyte_id, raw_name, lab_source)
                        VALUES (:id, :analyte_id, :raw_name, NULL)
                    """),
                    {"id": str(uuid.uuid4()), "analyte_id": analyte_id, "raw_name": raw_name},
                )
                inserted_aliases += 1

        # Upsert reference ranges
        for rr in entry.get("ref_ranges", []):
            existing = await db.execute(
                text("""
                    SELECT id FROM reference_ranges
                    WHERE analyte_id = :aid
                      AND (sex = :sex OR (sex IS NULL AND :sex IS NULL))
                      AND age_min_years IS NULL AND age_max_years IS NULL
                """),
                {"aid": analyte_id, "sex": rr.get("sex")},
            )
            if not existing.fetchone():
                await db.execute(
                    text("""
                        INSERT INTO reference_ranges
                            (id, analyte_id, unit, low_normal, high_normal, sex, source)
                        VALUES (:id, :analyte_id, :unit, :low, :high, :sex, :source)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "analyte_id": analyte_id,
                        "unit": entry["canonical_unit"],
                        "low": rr.get("low"),
                        "high": rr.get("high"),
                        "sex": rr.get("sex"),
                        "source": "Standard adult reference ranges",
                    },
                )
                inserted_ranges += 1

    await db.commit()
    print(f"Done: {inserted_analytes} analytes, {inserted_aliases} aliases, {inserted_ranges} reference ranges inserted.")


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as db:
        await seed(db)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
