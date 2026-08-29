"""Business transformations for the processed project register."""

import pandas as pd

from .config import (
    COLUMN_NAMES,
    CURRENT_PHASES,
    PROCUREMENT_STRATEGIES,
    VALUE_BANDS,
)


def standardise_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """Rename source columns for Python and Tableau."""

    return data.rename(columns=COLUMN_NAMES)


def decode_reference_values(data: pd.DataFrame) -> pd.DataFrame:
    """Add readable value, procurement, and phase definitions."""

    transformed = data.copy()
    transformed["estimated_value_band"] = transformed[
        "estimated_value_code"
    ].map(lambda code: VALUE_BANDS.get(code, {}).get("label"))
    transformed["value_minimum_aud_m"] = transformed[
        "estimated_value_code"
    ].map(lambda code: VALUE_BANDS.get(code, {}).get("minimum"))
    transformed["value_maximum_aud_m"] = transformed[
        "estimated_value_code"
    ].map(lambda code: VALUE_BANDS.get(code, {}).get("maximum"))
    transformed["procurement_strategy_name"] = transformed[
        "procurement_strategy_code"
    ].map(PROCUREMENT_STRATEGIES)
    transformed["current_phase_definition"] = transformed["current_phase"].map(
        CURRENT_PHASES
    )
    return transformed


def add_project_ids(data: pd.DataFrame) -> pd.DataFrame:
    """Sort the register and generate stable readable project IDs."""

    transformed = data.sort_values(by="project_name").reset_index(drop=True)
    transformed.insert(
        0,
        "project_id",
        [f"PRJ-{number:04d}" for number in range(1, len(transformed) + 1)],
    )
    return transformed
