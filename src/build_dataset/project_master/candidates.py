"""Generate possible matches between project data sources."""

from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd

from .config import MINIMUM_CANDIDATE_SCORE

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_key",
    "left_source_dataset",
    "left_source_project_id",
    "left_project_name",
    "right_source_dataset",
    "right_source_project_id",
    "right_project_name",
    "match_method",
    "similarity_score",
    "review_required",
]

def token_sort_text(value: str) -> str:
    """Sort words so that word order has less effect on matching."""

    return " ".join(sorted(value.split()))


def calculate_similarity(
    left_name: str,
    right_name: str,
) -> float:
    """Calculate similarity between two normalised names."""

    if not left_name or not right_name:
        return 0.0

    direct_score = SequenceMatcher(
        None,
        left_name,
        right_name,
    ).ratio()

    token_score = SequenceMatcher(
        None,
        token_sort_text(left_name),
        token_sort_text(right_name),
    ).ratio()

    return round(
        max(direct_score, token_score),
        4,
    )

def validate_candidate_input(
    data: pd.DataFrame,
) -> None:
    """Check that source records are ready for matching."""

    required_columns = {
        "source_dataset",
        "source_project_id",
        "source_project_name",
        "normalised_project_name",
    }

    missing_columns = required_columns.difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing candidate input columns: "
            + ", ".join(sorted(missing_columns))
        )

    if data.empty:
        raise ValueError(
            "No source projects were supplied."
        )

def build_source_record_key(
    record: dict,
) -> str:
    """Create a stable identity for one source record."""

    return (
        f"{record['source_dataset']}"
        f"::{record['source_project_id']}"
    )


def build_candidate_key(
    left: dict,
    right: dict,
) -> str:
    """Create a stable identity for a candidate pair."""

    record_keys = sorted(
        [
            build_source_record_key(left),
            build_source_record_key(right),
        ]
    )

    return "||".join(record_keys)

def generate_match_candidates(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Generate exact and fuzzy cross-source match candidates."""

    validate_candidate_input(data)

    records = data.to_dict(orient="records")
    candidate_rows = []

    for left, right in combinations(records, 2):
        # Never match records from the same source.
        if (
            left["source_dataset"]
            == right["source_dataset"]
        ):
            continue

        left_name = left["normalised_project_name"]
        right_name = right["normalised_project_name"]

        if left_name == right_name:
            match_method = "exact"
            similarity_score = 1.0
            review_required = False
        else:
            similarity_score = calculate_similarity(
                left_name,
                right_name,
            )

            if (
                similarity_score
                < MINIMUM_CANDIDATE_SCORE
            ):
                continue

            match_method = "fuzzy"
            review_required = True

        candidate_rows.append(
            {
                "candidate_key": build_candidate_key(
                    left,
                    right,
                ),
                "left_source_dataset": (
                    left["source_dataset"]
                ),
                "left_source_project_id": (
                    left["source_project_id"]
                ),
                "left_project_name": (
                    left["source_project_name"]
                ),
                "right_source_dataset": (
                    right["source_dataset"]
                ),
                "right_source_project_id": (
                    right["source_project_id"]
                ),
                "right_project_name": (
                    right["source_project_name"]
                ),
                "match_method": match_method,
                "similarity_score": similarity_score,
                "review_required": review_required,
            }
            
        )

    candidates = pd.DataFrame(candidate_rows)

    if candidates.empty:
        return pd.DataFrame(
            columns=CANDIDATE_COLUMNS
        )

    candidates = candidates.sort_values(
        by=[
            "match_method",
            "similarity_score",
            "left_source_dataset",
            "left_source_project_id",
            "right_source_dataset",
            "right_source_project_id",
        ],
        ascending=[
            True,
            False,
            True,
            True,
            True,
            True,
        ],
    ).reset_index(drop=True)

    candidates.insert(
        0,
        "candidate_id",
        [
            f"candidate_{number:04d}"
            for number in range(
                1,
                len(candidates) + 1,
            )
        ],
    )

    return candidates[CANDIDATE_COLUMNS]

