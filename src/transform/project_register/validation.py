"""Validation rules for the Infrastructure NSW project register."""

import pandas as pd

from .config import (
    CURRENT_PHASES,
    EXPECTED_PROJECTS,
    EXPECTED_SOURCE_RECORDS,
    LIFECYCLE_PRIORITY,
    PROCUREMENT_STRATEGIES,
    REQUIRED_COLUMNS,
    VALUE_BANDS,
)


def validate_input(data: pd.DataFrame) -> None:
    """Validate the interim Transport extract before transformation."""

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing_columns))
        )
    if len(data) != EXPECTED_SOURCE_RECORDS:
        raise ValueError(
            f"Expected {EXPECTED_SOURCE_RECORDS} source records, "
            f"but found {len(data)}."
        )
    if data["Project name"].isna().any():
        raise ValueError("One or more records have a missing project name.")

    invalid_sectors = data.loc[
        data["Sector"] != "Transport", "Sector"
    ].dropna().unique()
    if len(invalid_sectors) > 0:
        raise ValueError(
            "Non-Transport records found: "
            + ", ".join(sorted(invalid_sectors))
        )

    invalid_lifecycles = set(
        data["Source Lifecycle"].dropna().unique()
    ).difference(LIFECYCLE_PRIORITY)
    if invalid_lifecycles:
        raise ValueError(
            "Unexpected source lifecycles: "
            + ", ".join(sorted(invalid_lifecycles))
        )


def validate_reference_values(data: pd.DataFrame) -> None:
    """Detect source codes missing from the approved lookup dictionaries."""

    _raise_for_unknown_codes(
        data,
        source_column="estimated_value_code",
        decoded_column="estimated_value_band",
        label="Unknown value codes",
        reference_values=VALUE_BANDS,
    )
    _raise_for_unknown_codes(
        data,
        source_column="procurement_strategy_code",
        decoded_column="procurement_strategy_name",
        label="Unknown procurement strategies",
        reference_values=PROCUREMENT_STRATEGIES,
    )
    _raise_for_unknown_codes(
        data,
        source_column="current_phase",
        decoded_column="current_phase_definition",
        label="Unknown current phases",
        reference_values=CURRENT_PHASES,
    )


def _raise_for_unknown_codes(
    data: pd.DataFrame,
    source_column: str,
    decoded_column: str,
    label: str,
    reference_values: dict,
) -> None:
    """Raise a readable error when a populated source code cannot be decoded."""

    unknown_codes = data.loc[
        data[source_column].notna() & data[decoded_column].isna(), source_column
    ].unique()
    unknown_codes = [code for code in unknown_codes if code not in reference_values]
    if unknown_codes:
        raise ValueError(f"{label}: " + ", ".join(sorted(unknown_codes)))


def validate_output(data: pd.DataFrame) -> None:
    """Validate final record counts, identifiers, and project names."""

    if len(data) != EXPECTED_PROJECTS:
        raise ValueError(
            f"Expected {EXPECTED_PROJECTS} unique projects, but found {len(data)}."
        )
    if not data["project_id"].is_unique:
        raise ValueError("Project IDs are not unique.")
    if not data["project_name"].is_unique:
        raise ValueError("Project names are not unique.")
    if data["project_name"].isna().any():
        raise ValueError("The final register contains a missing project name.")
