"""Business transformations for Budget Paper project snapshots."""

import hashlib
import re
import unicodedata

import pandas as pd

from .config import AGENCY_GROUPS


FOOTNOTE_MARKER_PATTERN = re.compile(
    r"\([a-z]\)(?=\s|$)",
    flags=re.IGNORECASE,
)


def _clean_text(value: object) -> str | None:
    """Collapse whitespace and return None for empty source text."""

    if value is None or pd.isna(value):
        return None

    text = " ".join(str(value).split()).strip()
    return text or None


def _parse_money(value: object) -> tuple[int | None, bool]:
    """Convert a published $000 value while retaining disclosure status."""

    text = _clean_text(value)

    if text is None or text.casefold() == "n.a.":
        return None, False

    negative = text.startswith("(") and text.endswith(")")
    cleaned = text.strip("()$ ").replace(",", "")

    if not re.fullmatch(r"-?\d+(?:\.\d+)?", cleaned):
        raise ValueError(f"Unexpected financial value: {text}")

    number = int(float(cleaned))
    return (-number if negative else number), True


def _parse_year(value: object) -> tuple[int | None, bool]:
    """Return an integer year when the published period is a single year."""

    text = _normalise_period(value)

    if text is None or text.casefold() == "n.a.":
        return None, False

    if re.fullmatch(r"\d{4}", text):
        return int(text), True

    return None, True


def _normalise_period(value: object) -> str | None:
    """Normalise spacing artefacts in years and n.a. markers."""

    text = _clean_text(value)
    if text is None:
        return None

    compact = re.sub(r"\s+", "", text)

    if re.fullmatch(r"n\.a\.", compact, flags=re.IGNORECASE):
        return "n.a."
    if re.fullmatch(r"\d{4}", compact):
        return compact
    if compact.casefold() == "tbc":
        return "TBC"

    return text


def _normalise_project_name(project_name: str) -> str:
    """Build a comparable key without changing the published project name."""

    text = unicodedata.normalize("NFKC", project_name)
    text = text.replace("–", "-").replace("—", "-")
    text = FOOTNOTE_MARKER_PATTERN.sub("", text)
    text = re.sub(r"[^a-z0-9]+", " ", text.casefold())
    return " ".join(text.split())


def _project_id(match_key: str) -> str:
    """Generate a stable project identifier from the comparison key."""

    digest = hashlib.sha1(match_key.encode("utf-8")).hexdigest()[:10]
    return f"BUD-{digest.upper()}"


def transform_projects(project_rows: pd.DataFrame) -> pd.DataFrame:
    """Clean logical rows and create comparison-ready project snapshots."""

    transformed = project_rows.copy()

    text_columns = [
        "project_name",
        "agency",
        "work_category",
        "delivery_status",
        "program_group",
        "location",
        "start_period",
        "completion_period",
    ]
    for column in text_columns:
        transformed[column] = transformed[column].map(_clean_text)

    transformed["start_period"] = transformed["start_period"].map(
        _normalise_period
    )
    transformed["completion_period"] = transformed[
        "completion_period"
    ].map(_normalise_period)

    transformed["agency_group"] = transformed["agency"].map(
        AGENCY_GROUPS
    )

    cost_values = transformed[
        "estimated_total_cost_000_raw"
    ].map(_parse_money)
    transformed["estimated_total_cost_000"] = cost_values.map(
        lambda result: result[0]
    ).astype("Int64")
    transformed["total_cost_disclosed"] = cost_values.map(
        lambda result: result[1]
    )

    expenditure_values = transformed[
        "estimated_expenditure_000_raw"
    ].map(_parse_money)
    transformed[
        "estimated_expenditure_to_june_000"
    ] = expenditure_values.map(lambda result: result[0]).astype("Int64")
    transformed["expenditure_disclosed"] = expenditure_values.map(
        lambda result: result[1]
    )

    allocation_values = transformed[
        "annual_allocation_000_raw"
    ].map(_parse_money)
    transformed["annual_allocation_000"] = allocation_values.map(
        lambda result: result[0]
    ).astype("Int64")
    transformed["allocation_disclosed"] = allocation_values.map(
        lambda result: result[1]
    )

    start_values = transformed["start_period"].map(_parse_year)
    transformed["start_year"] = start_values.map(
        lambda result: result[0]
    ).astype("Int64")
    transformed["start_disclosed"] = start_values.map(
        lambda result: result[1]
    )

    completion_values = transformed["completion_period"].map(
        _parse_year
    )
    transformed["completion_year"] = completion_values.map(
        lambda result: result[0]
    ).astype("Int64")
    transformed["completion_disclosed"] = completion_values.map(
        lambda result: result[1]
    )

    normalised_names = transformed["project_name"].map(
        _normalise_project_name
    )
    transformed["project_match_key"] = (
        transformed["agency_group"].fillna(transformed["agency"])
        + "|"
        + normalised_names
    )
    transformed["project_id"] = transformed[
        "project_match_key"
    ].map(_project_id)
    transformed["snapshot_id"] = (
        transformed["project_id"]
        + "-"
        + transformed["budget_year"]
    )

    return transformed.sort_values(
        by=["project_id", "budget_year", "source_page"]
    ).reset_index(drop=True)
