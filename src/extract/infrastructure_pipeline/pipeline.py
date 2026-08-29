"""Orchestration for extracting the Infrastructure NSW workbook."""

import pandas as pd

from .config import INPUT_FILE, OUTPUT_FILE, SHEET_CONFIG
from .validation import (
    validate_output,
    validate_sheet,
    validate_source,
    validate_workbook_sheets,
)
from .workbook import load_transport_sheet


def run_pipeline() -> pd.DataFrame:
    """Extract, validate, save, and return the combined Transport records."""

    validate_source(INPUT_FILE)
    validate_workbook_sheets(INPUT_FILE)

    lifecycle_frames = []
    for sheet in SHEET_CONFIG:
        lifecycle_data = load_transport_sheet(
            INPUT_FILE,
            sheet_name=sheet["sheet_name"],
            lifecycle=sheet["lifecycle"],
        )
        validate_sheet(lifecycle_data, sheet["lifecycle"])
        lifecycle_frames.append(lifecycle_data)
        print(
            f"{sheet['lifecycle']} Transport records:",
            len(lifecycle_data),
        )

    combined = pd.concat(lifecycle_frames, ignore_index=True, sort=False)
    validate_output(combined)

    print("Combined Transport records:", len(combined))
    print("\nColumns:")
    for column in combined.columns:
        print("-", column)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print("\nFile created:")
    print(OUTPUT_FILE)
    return combined
