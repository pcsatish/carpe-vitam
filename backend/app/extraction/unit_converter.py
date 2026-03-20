"""Unit conversion for test results."""

import re


class UnitConverter:
    """Handles unit normalization and conversions."""

    # Conversion rules: (test_name_pattern, from_unit, multiplier, to_unit)
    CONVERSION_RULES = [
        # Standardize gm/dL -> g/dL
        (None, "gm/dL", 1.0, "g/dL"),
        (None, "gm/dl", 1.0, "g/dL"),

        # Lipids: mmol/L -> mg/dL
        ("CHOLESTEROL", "mmol/l", 38.67, "mg/dL"),
        ("TRIGLYCERIDES", "mmol/l", 88.57, "mg/dL"),

        # Default case: identity conversion
    ]

    @classmethod
    def convert(
        cls,
        raw_value: float | None,
        raw_unit: str,
        canonical_name: str | None = None,
    ) -> tuple[float | None, str]:
        """
        Convert raw value and unit to canonical unit.

        Args:
            raw_value: Numeric value
            raw_unit: Original unit string
            canonical_name: Test name for context-specific conversions

        Returns:
            (converted_value, canonical_unit)
        """
        if raw_value is None:
            return None, raw_unit or "unknown"

        unit = raw_unit.strip() if raw_unit else "unknown"

        # Default: no conversion
        converted_value = raw_value
        canonical_unit = unit

        # Try to find a conversion rule
        for test_pattern, from_unit, multiplier, to_unit in cls.CONVERSION_RULES:
            # Check unit match (case-insensitive)
            if from_unit.lower() == unit.lower():
                # If test_pattern is None, this rule applies to all tests
                if test_pattern is None:
                    converted_value = raw_value * multiplier
                    canonical_unit = to_unit
                    break
                # Otherwise, check if test name matches
                elif canonical_name and test_pattern in canonical_name.upper():
                    converted_value = raw_value * multiplier
                    canonical_unit = to_unit
                    break

        return converted_value, canonical_unit
