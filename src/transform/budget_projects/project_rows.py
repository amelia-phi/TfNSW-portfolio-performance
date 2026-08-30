"""Reconstruct project and total rows from visual table lines."""

import re

import pandas as pd

from .config import (
    AGENCY_ALIASES,
    CONTINUATION_MAX_GAP,
    DELIVERY_STATUSES,
    WORK_CATEGORIES,
)


VALUE_PATTERN = re.compile(
    r"^(?:n\.a\.|-?\d[\d,]*(?:\.\d+)?)$",
    flags=re.IGNORECASE,
)
FOOTNOTE_PATTERN = re.compile(r"^\([a-z0-9]+\)\s", re.IGNORECASE)
FOOTNOTE_SUFFIX_PATTERN = re.compile(
    r"(?:\([a-z]\))+\s*$",
    flags=re.IGNORECASE,
)


def _normalise_heading(text: str) -> str:
    """Normalise a heading for lookup while retaining its source value."""

    cleaned = FOOTNOTE_SUFFIX_PATTERN.sub("", text.strip())
    return " ".join(cleaned.casefold().split())


def _is_value(text: str) -> bool:
    """Return whether text is a source table value or n.a. marker."""

    return bool(VALUE_PATTERN.fullmatch(text.strip()))


def _is_anchor_line(line: dict) -> bool:
    """Identify a project or total row by its allocation value."""

    return _is_value(line["annual_allocation_000_raw"])


def _is_total_line(line: dict) -> bool:
    """Identify published total rows that are not individual projects."""

    project_name = line["project_name"].strip().casefold()
    return bool(re.match(r"^t\s*otal\s*,", project_name))


def _is_note(text: str) -> bool:
    """Identify footnotes and explanatory prose."""

    normalised = text.strip().casefold()
    return bool(FOOTNOTE_PATTERN.match(text.strip())) or normalised.startswith(
        ("note:", "source:", "development of ", "is the announced ")
    )


def _append_text(existing: str, additional: str) -> str:
    """Append wrapped text using a single space."""

    return " ".join(
        part.strip()
        for part in (existing, additional)
        if part and part.strip()
    )


def _match_agency(text: str) -> str | None:
    """Return the canonical published agency for a heading."""

    return AGENCY_ALIASES.get(" ".join(text.casefold().split()))


def _new_row(line: dict, context: dict, row_type: str) -> dict:
    """Create a logical project or total row from an anchor line."""

    return {
        "row_type": row_type,
        "budget_year": line["budget_year"],
        "government_sector": line["government_sector"],
        "agency": context["agency"],
        "work_category": context["work_category"],
        "delivery_status": context["delivery_status"],
        "program_group": context["program_group"],
        "project_name": line["project_name"],
        "location": line["location"],
        "start_period": line["start_period"],
        "completion_period": line["completion_period"],
        "estimated_total_cost_000_raw": line[
            "estimated_total_cost_000_raw"
        ],
        "estimated_expenditure_000_raw": line[
            "estimated_expenditure_000_raw"
        ],
        "annual_allocation_000_raw": line[
            "annual_allocation_000_raw"
        ],
        "source_file": line["source_file"],
        "source_page": line["page_number"],
        "source_row_top": line["line_top"],
        "last_line_top": line["line_top"],
    }


def _append_continuation(row: dict, line: dict) -> None:
    """Attach wrapped project-name and location text to a logical row."""

    row["project_name"] = _append_text(
        row["project_name"],
        line["project_name"],
    )
    row["location"] = _append_text(
        row["location"],
        line["location"],
    )
    row["last_line_top"] = line["line_top"]


def _finalise_row(row: dict | None, rows: list[dict]) -> None:
    """Append a completed row and remove its parsing-only state."""

    if row is None:
        return

    row.pop("last_line_top", None)
    rows.append(row)


def reconstruct_rows(
    visual_lines: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return reconstructed project rows and published total rows."""

    project_rows: list[dict] = []
    total_rows: list[dict] = []

    group_columns = [
        "budget_year",
        "government_sector",
        "source_file",
    ]

    for (_, government_sector, _), source_lines in (
        visual_lines.groupby(group_columns, sort=False)
    ):
        context = {
            "agency": (
                "Transport for NSW"
                if government_sector == "general_government"
                else None
            ),
            # The 2024-25 Transport pages omit these opening labels,
            # although their published closing totals confirm them.
            "work_category": (
                "Major Works"
                if government_sector == "general_government"
                else None
            ),
            "delivery_status": (
                "Works in Progress"
                if government_sector == "general_government"
                else None
            ),
            "program_group": None,
        }
        current_row = None
        last_structural_top = None
        last_structural_type = None

        for line in source_lines.to_dict("records"):
            if _is_anchor_line(line):
                _finalise_row(current_row, project_rows)
                current_row = None

                row_type = (
                    "total" if _is_total_line(line) else "project"
                )
                logical_row = _new_row(line, context, row_type)

                if row_type == "total":
                    _finalise_row(logical_row, total_rows)
                else:
                    current_row = logical_row

                last_structural_top = None
                last_structural_type = None
                continue

            non_value_fields = [
                line["project_name"],
                line["location"],
            ]
            has_other_values = any(
                line[column]
                for column in (
                    "start_period",
                    "completion_period",
                    "estimated_total_cost_000_raw",
                    "estimated_expenditure_000_raw",
                    "annual_allocation_000_raw",
                )
            )
            gap = (
                line["line_top"] - current_row["last_line_top"]
                if current_row is not None
                else None
            )

            if (
                current_row is not None
                and gap is not None
                and 0 < gap <= CONTINUATION_MAX_GAP
                and any(non_value_fields)
                and not has_other_values
            ):
                _append_continuation(current_row, line)
                continue

            _finalise_row(current_row, project_rows)
            current_row = None

            full_text = line["full_text"].strip()
            project_text = line["project_name"].strip()

            if not full_text or _is_note(full_text):
                continue

            agency = _match_agency(full_text)
            if agency:
                if agency != context["agency"]:
                    context.update(
                        {
                            "agency": agency,
                            "work_category": None,
                            "delivery_status": None,
                            "program_group": None,
                        }
                    )
                else:
                    context["agency"] = agency
                last_structural_top = line["line_top"]
                last_structural_type = "agency"
                continue

            heading_key = _normalise_heading(project_text)

            if heading_key in WORK_CATEGORIES:
                context["work_category"] = WORK_CATEGORIES[
                    heading_key
                ]
                context["delivery_status"] = None
                context["program_group"] = None
                last_structural_top = line["line_top"]
                last_structural_type = "work_category"
                continue

            if heading_key in DELIVERY_STATUSES:
                context["delivery_status"] = DELIVERY_STATUSES[
                    heading_key
                ]
                context["program_group"] = None
                last_structural_top = line["line_top"]
                last_structural_type = "delivery_status"
                continue

            if heading_key in {"transport", ""}:
                continue

            structural_gap = (
                line["line_top"] - last_structural_top
                if last_structural_top is not None
                else None
            )
            if (
                last_structural_type == "program_group"
                and structural_gap is not None
                and 0 < structural_gap <= CONTINUATION_MAX_GAP
            ):
                context["program_group"] = _append_text(
                    context["program_group"],
                    project_text,
                )
            elif project_text:
                context["program_group"] = project_text

            last_structural_top = line["line_top"]
            last_structural_type = "program_group"

        _finalise_row(current_row, project_rows)

    return pd.DataFrame(project_rows), pd.DataFrame(total_rows)
