"""Validation rules for the Infrastructure NSW workbook extraction."""

from pathlib import Path

import pandas as pd

from .config import (
    EXPECTED_OUTPUT_COLUMNS,
    EXPECTED_RECORDS_BY_LIFECYCLE,
    EXPECTED_TOTAL_RECORDS,
    SHEET_CONFIG,
)


def validate_source(input_file: Path) -> None:
    """Confirm that the expected Excel workbook exists."""

    if not input_file.exists():
        raise FileNotFoundError(f"Infrastructure workbook not found: {input_file}")
    if input_file.suffix.lower() != ".xlsx":
        raise ValueError("Infrastructure pipeline source is not an XLSX workbook.")


def validate_workbook_sheets(input_file: Path) -> None:
    """Confirm that all configured source sheets are present."""

    workbook = pd.ExcelFile(input_file)
    expected_sheets = {item["sheet_name"] for item in SHEET_CONFIG}
    missing_sheets = expected_sheets.difference(workbook.sheet_names)
    if missing_sheets:
        raise ValueError(
            "Workbook is missing sheets: " + ", ".join(sorted(missing_sheets))
        )


def validate_sheet(data: pd.DataFrame, lifecycle: str) -> None:
    """Validate the expected Transport count for one lifecycle."""

    expected_records = EXPECTED_RECORDS_BY_LIFECYCLE[lifecycle]
    if len(data) != expected_records:
        raise ValueError(
            f"Expected {expected_records} {lifecycle} Transport records, "
            f"but found {len(data)}."
        )


def validate_output(data: pd.DataFrame) -> None:
    """Validate final record count, schema, sector, and lifecycle completeness."""

    if len(data) != EXPECTED_TOTAL_RECORDS:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL_RECORDS} combined Transport records, "
            f"but found {len(data)}."
        )

    actual_columns = tuple(data.columns)
    if actual_columns != EXPECTED_OUTPUT_COLUMNS:
        raise ValueError(
            "Unexpected output columns. Expected: "
            + ", ".join(EXPECTED_OUTPUT_COLUMNS)
        )
    if data["Project name"].isna().any():
        raise ValueError("One or more Transport records have no project name.")
