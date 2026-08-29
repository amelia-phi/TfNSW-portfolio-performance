"""Validation rules for the TfNSW project timeline transformation."""

import pandas as pd

from .config import (
    EXPECTED_PAGES,
    EXPECTED_PROJECTS,
    EXPECTED_TIMELINE_SEGMENTS,
)


def validate_input(
    data: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    """Check that an extracted dataset has the required structure."""

    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing columns: "
            + ", ".join(sorted(missing_columns))
        )
    if data.empty:
        raise ValueError(f"{dataset_name} contains no records.")

    actual_pages = set(data["page_number"].unique())
    if actual_pages != EXPECTED_PAGES:
        raise ValueError(f"{dataset_name} does not contain pages 1 to 9.")


def validate_output(
    project_rows: pd.DataFrame,
    project_timeline: pd.DataFrame,
) -> None:
    """Check record counts, uniqueness, and timeline period integrity."""

    if len(project_rows) != EXPECTED_PROJECTS:
        raise ValueError(
            f"Expected {EXPECTED_PROJECTS} project rows, "
            f"but found {len(project_rows)}."
        )
    if project_rows["project_name"].duplicated().any():
        raise ValueError("Duplicated project names were found.")

    represented_projects = project_timeline["tfnsw_project_id"].nunique()
    if represented_projects != EXPECTED_PROJECTS:
        raise ValueError(
            f"Expected timeline records for {EXPECTED_PROJECTS} projects, "
            f"but found {represented_projects}."
        )
    if len(project_timeline) != EXPECTED_TIMELINE_SEGMENTS:
        raise ValueError(
            f"Expected {EXPECTED_TIMELINE_SEGMENTS} timeline segments, "
            f"but found {len(project_timeline)}."
        )

    invalid_periods = project_timeline[
        project_timeline["end_quarter_index"]
        < project_timeline["start_quarter_index"]
    ]
    if not invalid_periods.empty:
        raise ValueError("Timeline records with invalid periods were found.")

    duplicate_segments = project_timeline.duplicated(
        subset=[
            "tfnsw_project_id",
            "stage_name",
            "timing_status",
            "start_quarter",
            "end_quarter",
        ]
    )
    if duplicate_segments.any():
        raise ValueError("Duplicated timeline segments were found.")
