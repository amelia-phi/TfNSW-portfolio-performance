"""Duplicate detection, resolution, and assurance logging."""

import pandas as pd

from .config import EXPECTED_DUPLICATE_NAMES, LIFECYCLE_PRIORITY


def identify_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """Return all source rows whose project name occurs more than once."""

    duplicate_mask = data.duplicated(subset=["Project name"], keep=False)
    return data[duplicate_mask].sort_values(
        by=["Project name", "Source Lifecycle"]
    )


def validate_duplicates(duplicates: pd.DataFrame) -> None:
    """Confirm that only the reviewed cross-category duplicate is present."""

    actual_duplicate_names = set(duplicates["Project name"].unique())
    if actual_duplicate_names != EXPECTED_DUPLICATE_NAMES:
        raise ValueError(
            "The duplicate projects differ from the reviewed source condition. "
            "Review them before continuing."
        )


def consolidate_projects(data: pd.DataFrame) -> pd.DataFrame:
    """Prioritise Pipeline and retain one record per unique project."""

    prioritised = data.copy()
    prioritised["lifecycle_priority"] = (
        prioritised["Source Lifecycle"].map(LIFECYCLE_PRIORITY).fillna(99)
    )
    project_register = prioritised.sort_values(
        by=["Project name", "lifecycle_priority"]
    ).drop_duplicates(subset=["Project name"], keep="first")
    return project_register.drop(columns=["lifecycle_priority"])


def build_duplicate_log(duplicates: pd.DataFrame) -> pd.DataFrame:
    """Create the reviewed data-quality exception record."""

    duplicate_summary = (
        duplicates.groupby("Project name")
        .size()
        .rename("records_found")
        .reset_index()
        .rename(columns={"Project name": "project_name"})
    )
    duplicate_summary.insert(0, "rule_id", "DQ001")
    duplicate_summary["issue"] = (
        "Project appears in both Pipeline and In Planning"
    )
    duplicate_summary["resolution"] = (
        "Retained the Pipeline record because it contains the more complete "
        "phase, procurement and timeline information"
    )
    duplicate_summary["validation_evidence"] = (
        "Infrastructure NSW live In Planning search returned no matching "
        "project on 2026-08-29"
    )
    return duplicate_summary
