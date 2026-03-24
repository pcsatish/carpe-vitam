"""
Seed missing analytes and aliases discovered via audit_unrecognized.py.

Adds CBC panel, vitamins, additional hormones, cardiac markers, and
missing aliases for existing catalog entries (T3, T4, TSH, eGFR, etc.).

Safe to run multiple times — skips entries that already exist.

Run from backend/ directory:
    python -m scripts.seed_missing_analytes
"""

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.analyte import AnalyteCatalog, AnalyteAlias


# ─── Catalog definition ──────────────────────────────────────────────────────
# Each entry: canonical_name, category, canonical_unit, [normalized aliases]
# Aliases are the output of Canonicalizer.normalize_name() on raw PDF text.
# For existing catalog entries, use canonical_name="" to skip creation and
# only add aliases — handled by lookup below.

ANALYTES: list[dict] = [
    # ── CBC ──────────────────────────────────────────────────────────────────
    {
        "canonical_name": "Hemoglobin",
        "category": "Hematology",
        "canonical_unit": "g/dL",
        "aliases": [
            "HEMOGLOBIN",
            "HEMOGLOBIN SLS HEMOGLOBIN METHOD",
        ],
    },
    {
        "canonical_name": "WBC",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "TOTAL LEUCOCYTES COUNT WBC",
            "TOTAL LEUCOCYTE COUNT WBC",
            "TOTAL LEUCOCYTE COUNT WBC HF FC",
            "TOTAL LEUCOCYTES COUNT WBC HF FC",
        ],
    },
    {
        "canonical_name": "RBC",
        "category": "Hematology",
        "canonical_unit": "X 10⁶/µL",
        "aliases": [
            "TOTAL RBC",
            "TOTAL RBC HF EI",
        ],
    },
    {
        "canonical_name": "Platelet Count",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "PLATELET COUNT",
            "PLATELET COUNT HF EI",
        ],
    },
    {
        "canonical_name": "MCV",
        "category": "Hematology",
        "canonical_unit": "fL",
        "aliases": [
            "MEAN CORPUSCULAR VOLUME MCV",
        ],
    },
    {
        "canonical_name": "MCH",
        "category": "Hematology",
        "canonical_unit": "pg",
        "aliases": [
            "MEAN CORPUSCULAR HEMOGLOBIN MCH",
        ],
    },
    {
        "canonical_name": "MCHC",
        "category": "Hematology",
        "canonical_unit": "g/dL",
        "aliases": [
            "MEAN CORP HEMO CONC MCHC",
        ],
    },
    {
        "canonical_name": "Hematocrit",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "HEMATOCRIT PCV",
            "HEMATOCRIT PCV CPH DETECTION",
        ],
    },
    {
        "canonical_name": "Neutrophils",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "NEUTROPHILS",
            "NEUTROPHILS PERCENTAGE FLOW CYTOMETRY",
            "NEUTROPHILS FLOW CYTOMETRY",
        ],
    },
    {
        "canonical_name": "Lymphocytes",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "LYMPHOCYTE",
            "LYMPHOCYTE PERCENTAGE",
            "LYMPHOCYTES PERCENTAGE FLOW CYTOMETRY",
            "LYMPHOCYTE FLOW CYTOMETRY",
        ],
    },
    {
        "canonical_name": "Monocytes",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "MONOCYTES",
            "MONOCYTES PERCENTAGE FLOW CYTOMETRY",
            "MONOCYTES FLOW CYTOMETRY",
        ],
    },
    {
        "canonical_name": "Basophils",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "BASOPHILS",
            "BASOPHILS PERCENTAGE FLOW CYTOMETRY",
            "BASOPHILS FLOW CYTOMETRY",
        ],
    },
    {
        "canonical_name": "Eosinophils",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "EOSINOPHILS",
            "EOSINOPHILS PERCENTAGE FLOW CYTOMETRY",
            "EOSINOPHILS FLOW CYTOMETRY",
        ],
    },
    {
        "canonical_name": "Neutrophils Absolute",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "NEUTROPHILS ABSOLUTE COUNT",
        ],
    },
    {
        "canonical_name": "Lymphocytes Absolute",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "LYMPHOCYTES ABSOLUTE COUNT",
        ],
    },
    {
        "canonical_name": "Monocytes Absolute",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "MONOCYTES ABSOLUTE COUNT",
        ],
    },
    {
        "canonical_name": "Basophils Absolute",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "BASOPHILS ABSOLUTE COUNT",
        ],
    },
    {
        "canonical_name": "Eosinophils Absolute",
        "category": "Hematology",
        "canonical_unit": "X 10³/µL",
        "aliases": [
            "EOSINOPHILS ABSOLUTE COUNT",
        ],
    },
    {
        "canonical_name": "RDW-CV",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "RED CELL DISTRIBUTION WIDTH RDW CV",
        ],
    },
    {
        "canonical_name": "MPV",
        "category": "Hematology",
        "canonical_unit": "fL",
        "aliases": [
            "MEAN PLATELET VOLUME MPV",
        ],
    },
    {
        "canonical_name": "Ferritin",
        "category": "Hematology",
        "canonical_unit": "ng/mL",
        "aliases": [
            "FERRITIN",
        ],
    },
    {
        "canonical_name": "Transferrin Saturation",
        "category": "Hematology",
        "canonical_unit": "%",
        "aliases": [
            "TRANSFERRIN SATURATION",
        ],
    },
    # ── HbA1c ────────────────────────────────────────────────────────────────
    {
        "canonical_name": "HbA1c",
        "category": "Glucose",
        "canonical_unit": "%",
        "aliases": [
            "HBA1C HPLC",
        ],
    },
    # ── Electrolytes ─────────────────────────────────────────────────────────
    {
        "canonical_name": "Potassium",
        "category": "Electrolyte",
        "canonical_unit": "mEq/L",
        "aliases": [
            "POTASSIUM",  # ISE suffix stripped by canonicalizer
        ],
    },
    {
        "canonical_name": "Phosphorus",
        "category": "Electrolyte",
        "canonical_unit": "mg/dL",
        "aliases": [
            "PHOSPHOROUS",
            "PHOSPHORUS",
        ],
    },
    # ── Vitamins ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "Vitamin B12",
        "category": "Vitamins",
        "canonical_unit": "pg/mL",
        "aliases": [
            "VITAMIN B 12",
            "VITAMIN B 12 CLIA",  # in case suffix strip misses edge cases
            "VITAMIN B 12 ECLIA",
        ],
    },
    {
        "canonical_name": "Vitamin D (Total)",
        "category": "Vitamins",
        "canonical_unit": "ng/mL",
        "aliases": [
            "25 OH VITAMIN D TOTAL",
            "25 OH VITAMIN D TOTAL CLIA",
            "25 OH VITAMIN D TOTAL ECLIA",
        ],
    },
    # ── Cardiac ──────────────────────────────────────────────────────────────
    {
        "canonical_name": "hs-CRP",
        "category": "Cardiac",
        "canonical_unit": "mg/L",
        "aliases": [
            "HIGH SENSITIVITY C REACTIVE PROTEIN HS CRP",
        ],
    },
    {
        "canonical_name": "CPK",
        "category": "Cardiac",
        "canonical_unit": "U/L",
        "aliases": [
            "CREATINE PHOSPHOKINASE CPK SERUM",
        ],
    },
    {
        "canonical_name": "Troponin I",
        "category": "Cardiac",
        "canonical_unit": "ng/mL",
        "aliases": [
            "TROPONIN I HEART ATTACK RISK",
        ],
    },
    {
        "canonical_name": "Homocysteine",
        "category": "Cardiac",
        "canonical_unit": "µmol/L",
        "aliases": [
            "HOMOCYSTEINE",
        ],
    },
    # ── Hormones ─────────────────────────────────────────────────────────────
    {
        "canonical_name": "DHEA-S",
        "category": "Hormones",
        "canonical_unit": "µg/dL",
        "aliases": [
            "DHEA SULPHATE DHEAS",
        ],
    },
    {
        "canonical_name": "Estradiol",
        "category": "Hormones",
        "canonical_unit": "pg/mL",
        "aliases": [
            "ESTRADIOL OESTROGEN E2",
        ],
    },
    {
        "canonical_name": "FSH",
        "category": "Hormones",
        "canonical_unit": "mIU/mL",
        "aliases": [
            "FOLLICLE STIMULATING HORMONE FSH",
        ],
    },
    {
        "canonical_name": "LH",
        "category": "Hormones",
        "canonical_unit": "mIU/mL",
        "aliases": [
            "LUTEINISING HORMONE LH",
        ],
    },
    {
        "canonical_name": "Prolactin",
        "category": "Hormones",
        "canonical_unit": "ng/mL",
        "aliases": [
            "PROLACTIN PRL",
        ],
    },
    {
        "canonical_name": "Progesterone",
        "category": "Hormones",
        "canonical_unit": "ng/mL",
        "aliases": [
            "PROGESTERONE",
        ],
    },
    {
        "canonical_name": "Insulin (Fasting)",
        "category": "Hormones",
        "canonical_unit": "µIU/mL",
        "aliases": [
            "INSULIN FASTING",
        ],
    },
    # ── Renal ────────────────────────────────────────────────────────────────
    {
        "canonical_name": "Urine Protein",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "PROTEIN URINE",
        ],
    },
    {
        "canonical_name": "Urine Creatinine",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "CREATININE URINE",
        ],
    },
    {
        "canonical_name": "Urine Microalbumin",
        "category": "Renal",
        "canonical_unit": "mg/L",
        "aliases": [
            "URINARY MICROALBUMIN",
        ],
    },
    {
        "canonical_name": "Cystatin C",
        "category": "Renal",
        "canonical_unit": "mg/L",
        "aliases": [
            "CYSTATIN C",
        ],
    },
    # ── Missing aliases for existing catalog entries ──────────────────────────
    # T3 (canonical_name="T3" already in catalog)
    {
        "canonical_name": "T3",
        "category": "Thyroid",
        "canonical_unit": "ng/dL",
        "aliases": [
            "T3",
            "TOTAL TRIIODOTHYRONINE T3",
        ],
    },
    # T4
    {
        "canonical_name": "T4",
        "category": "Thyroid",
        "canonical_unit": "µg/dL",
        "aliases": [
            "T4",
            "TOTAL THYROXINE T4",
        ],
    },
    # TSH
    {
        "canonical_name": "TSH",
        "category": "Thyroid",
        "canonical_unit": "µIU/mL",
        "aliases": [
            "TSH",
            "THYROID STIMULATING HORMONE TSH",
            "TSH ULTRASENSITIVE",
        ],
    },
    # eGFR
    {
        "canonical_name": "eGFR",
        "category": "Renal",
        "canonical_unit": "mL/min/1.73m²",
        "aliases": [
            "EGFR",
            "EST GLOMERULAR FILTRATION RATE EGFR",
        ],
    },
    # Urea
    {
        "canonical_name": "Urea",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "UREA",
        ],
    },
    # BUN
    {
        "canonical_name": "BUN",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "BUN",
            "BLOOD UREA NITROGEN BUN",
        ],
    },
    # Creatinine
    {
        "canonical_name": "Creatinine",
        "category": "Renal",
        "canonical_unit": "mg/dL",
        "aliases": [
            "CREATININE",
            "CREATININE SERUM",
        ],
    },
    # Cholesterol/Lipid aliases
    {
        "canonical_name": "Total Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "TOTAL CHOLESTEROL",
        ],
    },
    {
        "canonical_name": "HDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "HDL CHOLESTEROL",
            "HDL CHOLESTEROL DIRECT",
        ],
    },
    {
        "canonical_name": "LDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "LDL CHOLESTEROL",
            "LDL CHOLESTEROL DIRECT",
        ],
    },
    {
        "canonical_name": "Triglycerides",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "TRIGLYCERIDES",
        ],
    },
    {
        "canonical_name": "VLDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "VLDL CHOLESTEROL",
        ],
    },
    {
        "canonical_name": "Non-HDL Cholesterol",
        "category": "Lipid",
        "canonical_unit": "mg/dL",
        "aliases": [
            "NON HDL CHOLESTEROL",
        ],
    },
    # Liver aliases
    {
        "canonical_name": "ALT (SGPT)",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "ALANINE TRANSAMINASE SGPT",
            "ALT SGPT",
        ],
    },
    {
        "canonical_name": "AST (SGOT)",
        "category": "Liver",
        "canonical_unit": "U/L",
        "aliases": [
            "ASPARTATE AMINOTRANSFERASE SGOT",
            "AST SGOT",
        ],
    },
    {
        "canonical_name": "Albumin",
        "category": "Liver",
        "canonical_unit": "g/dL",
        "aliases": [
            "ALBUMIN",
            "ALBUMIN SERUM",
        ],
    },
    {
        "canonical_name": "Total Protein",
        "category": "Liver",
        "canonical_unit": "g/dL",
        "aliases": [
            "TOTAL PROTEIN",
            "PROTEIN TOTAL",
        ],
    },
]


async def main() -> None:
    added_analytes = 0
    added_aliases = 0

    async with AsyncSessionLocal() as db:
        for entry in ANALYTES:
            canonical_name = entry["canonical_name"]
            category = entry["category"]
            canonical_unit = entry["canonical_unit"]
            aliases = entry["aliases"]

            # Get or create catalog entry
            result = await db.execute(
                select(AnalyteCatalog).where(AnalyteCatalog.canonical_name == canonical_name)
            )
            analyte = result.scalar_one_or_none()

            if not analyte:
                analyte = AnalyteCatalog(
                    id=str(uuid.uuid4()),
                    canonical_name=canonical_name,
                    category=category,
                    canonical_unit=canonical_unit,
                    is_active=True,
                )
                db.add(analyte)
                await db.flush()  # get the id before adding aliases
                added_analytes += 1

            # Add missing aliases
            for raw_name in aliases:
                result = await db.execute(
                    select(AnalyteAlias).where(
                        AnalyteAlias.raw_name == raw_name,
                        AnalyteAlias.analyte_id == analyte.id,
                    )
                )
                if not result.scalar_one_or_none():
                    db.add(
                        AnalyteAlias(
                            id=str(uuid.uuid4()),
                            analyte_id=analyte.id,
                            raw_name=raw_name,
                            lab_source=None,
                        )
                    )
                    added_aliases += 1

        await db.commit()

    print(f"Done. Added {added_analytes} analytes, {added_aliases} aliases.")


if __name__ == "__main__":
    asyncio.run(main())
