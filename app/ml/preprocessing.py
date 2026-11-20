"""
Machine Learning Preprocessing Pipeline.
Handles feature extraction, imputation of missing values, ordinal encoding, and input validation.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


# Expected numerical and categorical feature mappings
CATEGORICAL_MAPPINGS = {
    "internet_access": {"none": 0, "poor": 1, "moderate": 2, "good": 3},
    "class_participation": {"low": 1, "medium": 2, "high": 3},
    "parental_education": {"primary": 1, "secondary": 2, "tertiary": 3, "postgraduate": 4},
    "stress_level": {"low": 1, "moderate": 2, "high": 3, "extreme": 4},
    "financial_support": {"inadequate": 1, "adequate": 2, "abundant": 3},
}

FEATURE_COLUMNS: List[str] = [
    "study_hours_per_week",
    "attendance_rate_pct",
    "sleep_hours_per_night",
    "travel_time_minutes",
    "social_media_hours_per_day",
    "participates_extracurricular",
    "internet_access_encoded",
    "class_participation_encoded",
    "parental_education_encoded",
    "stress_level_encoded",
    "financial_support_encoded",
    "current_level",
    "cumulative_gpa",
]

DEFAULT_VALUES: Dict[str, Any] = {
    "study_hours_per_week": 10.0,
    "attendance_rate_pct": 75.0,
    "sleep_hours_per_night": 7.0,
    "travel_time_minutes": 30,
    "social_media_hours_per_day": 2.0,
    "participates_extracurricular": 0,
    "internet_access_encoded": 2,  # moderate
    "class_participation_encoded": 2,  # medium
    "parental_education_encoded": 2,  # secondary
    "stress_level_encoded": 2,  # moderate
    "financial_support_encoded": 2,  # adequate
    "current_level": 100,
    "cumulative_gpa": 3.0,
}


def categorize_gpa(gpa: float, max_scale: float = 5.0) -> str:
    """
    Maps a numerical GPA to institutional performance classification tiers.
    Standard Nigerian / Commonwealth 5.0 grading scale:
    - 4.50 to 5.00: First Class Honours
    - 3.50 to 4.49: Second Class Honours (Upper Division)
    - 2.40 to 3.49: Second Class Honours (Lower Division)
    - 1.50 to 2.39: Third Class Honours
    - Below 1.50: At-Risk / Pass / Probation
    """
    if gpa >= 4.50:
        return "First Class Honours"
    elif gpa >= 3.50:
        return "Second Class Upper"
    elif gpa >= 2.40:
        return "Second Class Lower"
    elif gpa >= 1.50:
        return "Third Class"
    else:
        return "At-Risk / Academic Probation"


class MLPreprocessor:
    """
    Transforms raw backend student dictionary into an ML-ready Pandas DataFrame.
    """

    @classmethod
    def validate_raw_features(cls, raw: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates feature bounds and detects anomalies in inputs.
        """
        errors = []

        if "attendance_rate_pct" in raw and raw["attendance_rate_pct"] is not None:
            val = float(raw["attendance_rate_pct"])
            if val < 0.0 or val > 100.0:
                errors.append(f"attendance_rate_pct must be between 0.0 and 100.0, got {val}")

        if "study_hours_per_week" in raw and raw["study_hours_per_week"] is not None:
            val = float(raw["study_hours_per_week"])
            if val < 0.0 or val > 168.0:
                errors.append(f"study_hours_per_week cannot exceed 168 hours, got {val}")

        if "sleep_hours_per_night" in raw and raw["sleep_hours_per_night"] is not None:
            val = float(raw["sleep_hours_per_night"])
            if val < 0.0 or val > 24.0:
                errors.append(f"sleep_hours_per_night cannot exceed 24 hours, got {val}")

        return len(errors) == 0, errors

    @classmethod
    def transform(cls, raw_features: Dict[str, Any]) -> pd.DataFrame:
        """
        Transforms and imputes missing raw features into an ordered DataFrame.
        """
        processed: Dict[str, Any] = {}

        # 1. Numerical extraction with default fallback imputation
        for num_col in [
            "study_hours_per_week",
            "attendance_rate_pct",
            "sleep_hours_per_night",
            "travel_time_minutes",
            "social_media_hours_per_day",
            "current_level",
            "cumulative_gpa",
        ]:
            val = raw_features.get(num_col)
            if val is not None:
                try:
                    processed[num_col] = float(val)
                except (ValueError, TypeError):
                    processed[num_col] = DEFAULT_VALUES[num_col]
            else:
                processed[num_col] = DEFAULT_VALUES[num_col]

        # 2. Extracurricular flag
        extra = raw_features.get("participates_extracurricular")
        processed["participates_extracurricular"] = 1 if bool(extra) else 0

        # 3. Categorical encoding
        for cat_field, mapping in CATEGORICAL_MAPPINGS.items():
            encoded_key = f"{cat_field}_encoded"
            raw_val = str(raw_features.get(cat_field, "")).strip().lower()
            processed[encoded_key] = mapping.get(raw_val, DEFAULT_VALUES[encoded_key])

        # 4. Construct DataFrame matching strictly expected column order
        df = pd.DataFrame([processed], columns=FEATURE_COLUMNS)
        return df
