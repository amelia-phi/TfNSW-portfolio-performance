"""Validation rules for Budget Paper project snapshots."""

import pandas as pd

from .config import (
    AGENCY_GROUPS,
    FINAL_COLUMN_ORDER,
    REQUIRED_INPUT_COLUMNS,
)


def validate_input(data: pd.DataFrame) -> None:
    """Validate the positioned-word extract before transformation."""

    missing_columns = REQUIRED_INPUT_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "Missing input columns: "
            + ", ".join(sorted(missing_columns))
        )
    if data.empty:
        raise ValueError("The positioned-word extract is empty.")
    if data["text"].astype(str).str.strip().eq("").any():
        raise ValueError("The input contains blank word records.")


def validate_output(data: pd.DataFrame) -> None:
    """Validate final snapshot identifiers, values, and dimensions."""

    missing_columns = set(FINAL_COLUMN_ORDER).difference(data.columns)
    if missing_columns:
        raise ValueError(
            "Missing output columns: "
            + ", ".join(sorted(missing_columns))
        )
    if data.empty:
        raise ValueError("No project snapshots were reconstructed.")
    if data["project_name"].isna().any():
        raise ValueError("One or more projects have no project name.")
    if data["agency"].isna().any():
        raise ValueError("One or more projects have no agency.")
    unknown_agencies = set(data["agency"].unique()).difference(
        AGENCY_GROUPS
    )
    if unknown_agencies:
        raise ValueError(
            "Unknown agencies: "
            + ", ".join(sorted(unknown_agencies))
        )
    if not data["snapshot_id"].is_unique:
        duplicates = data.loc[
            data["snapshot_id"].duplicated(keep=False),
            ["snapshot_id", "project_name", "agency", "budget_year"],
        ]
        raise ValueError(
            "Duplicate project snapshots found:\n"
            + duplicates.to_string(index=False)
        )
    for column in (
        "estimated_total_cost_000",
        "estimated_expenditure_to_june_000",
        "annual_allocation_000",
    ):
        if data[column].dropna().lt(0).any():
            raise ValueError(f"Negative values found in {column}.")

    for period_column, year_column, disclosed_column in (
        ("start_period", "start_year", "start_disclosed"),
        (
            "completion_period",
            "completion_year",
            "completion_disclosed",
        ),
    ):
        missing_period = (
            data[period_column].isna()
            | data[period_column].astype(str).str.casefold().eq("n.a.")
        )
        disclosure_mismatch = missing_period.eq(
            data[disclosed_column]
        )
        if disclosure_mismatch.any():
            raise ValueError(
                f"Disclosure flags do not agree with {period_column}."
            )

        numeric_period = data[period_column].astype(str).str.fullmatch(
            r"\d{4}"
        )
        parsed_year = pd.to_numeric(
            data[year_column],
            errors="coerce",
        )
        inconsistent_year = numeric_period & (
            parsed_year != pd.to_numeric(
                data.loc[numeric_period, period_column],
                errors="coerce",
            ).reindex(data.index)
        )
        if inconsistent_year.any():
            raise ValueError(
                f"Parsed years do not agree with {period_column}."
            )


def _parse_total_value(value: object) -> int:
    """Convert a published total allocation from $000 text."""

    text = str(value).strip().replace(",", "")
    if not text.isdigit():
        raise ValueError(f"Unexpected published total value: {value}")
    return int(text)


def validate_allocation_totals(
    projects: pd.DataFrame,
    total_rows: pd.DataFrame,
) -> None:
    """Reconcile project allocations to published category totals."""

    total_name_by_category = {
        "Major Works": "Total, Major Works",
        "Leases": "Total, Leases",
    }
    exceptions = []

    for (budget_year, agency), agency_projects in projects.groupby(
        ["budget_year", "agency"]
    ):
        categories = set(agency_projects["work_category"].dropna())
        expected_total_names = {
            total_name_by_category[category]
            for category in categories
            if category in total_name_by_category
        }
        matching_totals = total_rows.loc[
            (total_rows["budget_year"] == budget_year)
            & (total_rows["agency"] == agency)
            & total_rows["project_name"].isin(expected_total_names)
        ]

        found_names = set(matching_totals["project_name"])
        missing_names = expected_total_names.difference(found_names)
        if missing_names:
            exceptions.append(
                {
                    "budget_year": budget_year,
                    "agency": agency,
                    "issue": (
                        "Missing published totals: "
                        + ", ".join(sorted(missing_names))
                    ),
                }
            )
            continue

        published_total = matching_totals[
            "annual_allocation_000_raw"
        ].map(_parse_total_value).sum()
        project_total = agency_projects[
            "annual_allocation_000"
        ].sum()

        if project_total != published_total:
            exceptions.append(
                {
                    "budget_year": budget_year,
                    "agency": agency,
                    "issue": (
                        f"Projects sum to {project_total:,}; "
                        f"published total is {published_total:,}."
                    ),
                }
            )

    if exceptions:
        raise ValueError(
            "Allocation reconciliation failed:\n"
            + pd.DataFrame(exceptions).to_string(index=False)
        )
