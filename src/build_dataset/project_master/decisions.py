"""Create, validate, and apply project-matching decisions."""

import pandas as pd


VALID_DECISIONS = {
    "pending",
    "approved",
    "rejected",
}


DECISION_COLUMNS = [
    "candidate_key",
    "left_source_dataset",
    "left_source_project_id",
    "left_project_name",
    "right_source_dataset",
    "right_source_project_id",
    "right_project_name",
    "similarity_score",
    "decision",
    "reviewer_notes",
]


def create_decision_template(
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Create a review table for fuzzy candidates."""

    required_columns = {
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
    }

    missing_columns = required_columns.difference(
        candidates.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing candidate columns: "
            + ", ".join(sorted(missing_columns))
        )

    fuzzy_candidates = candidates.loc[
        candidates["review_required"],
        [
            "candidate_key",
            "left_source_dataset",
            "left_source_project_id",
            "left_project_name",
            "right_source_dataset",
            "right_source_project_id",
            "right_project_name",
            "similarity_score",
        ],
    ].copy()

    fuzzy_candidates["decision"] = "pending"
    fuzzy_candidates["reviewer_notes"] = ""

    return fuzzy_candidates[DECISION_COLUMNS]


def validate_match_decisions(
    decisions: pd.DataFrame,
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Validate and standardise manual matching decisions."""

    required_columns = {
        "candidate_key",
        "decision",
    }

    missing_columns = required_columns.difference(
        decisions.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing decision columns: "
            + ", ".join(sorted(missing_columns))
        )

    validated = decisions.copy()

    validated["candidate_key"] = (
        validated["candidate_key"]
        .astype("string")
        .str.strip()
    )

    validated["decision"] = (
        validated["decision"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    duplicate_keys = validated[
        "candidate_key"
    ].duplicated(keep=False)

    if duplicate_keys.any():
        raise ValueError(
            "Duplicate candidate keys found in "
            "the matching decisions."
        )

    invalid_decisions = set(
        validated["decision"].dropna().unique()
    ).difference(VALID_DECISIONS)

    if invalid_decisions:
        raise ValueError(
            "Invalid matching decisions: "
            + ", ".join(sorted(invalid_decisions))
        )

    reviewable_keys = set(
        candidates.loc[
            candidates["review_required"],
            "candidate_key",
        ]
    )

    unknown_keys = set(
        validated["candidate_key"]
    ).difference(reviewable_keys)

    if unknown_keys:
        raise ValueError(
            "Decision file contains unknown or "
            "non-reviewable candidate keys."
        )

    return validated


def select_accepted_matches(
    candidates: pd.DataFrame,
    decisions: pd.DataFrame,
) -> pd.DataFrame:
    """Return exact and manually approved project links."""

    validated_decisions = validate_match_decisions(
        decisions,
        candidates,
    )

    exact_matches = candidates.loc[
        candidates["match_method"] == "exact"
    ].copy()

    exact_matches["match_decision"] = "approved"
    exact_matches["approval_method"] = (
        "exact_normalised_name"
    )

    approved_keys = set(
        validated_decisions.loc[
            validated_decisions["decision"]
            == "approved",
            "candidate_key",
        ]
    )

    approved_fuzzy_matches = candidates.loc[
        (
            candidates["match_method"]
            == "fuzzy"
        )
        & candidates["candidate_key"].isin(
            approved_keys
        )
    ].copy()

    approved_fuzzy_matches[
        "match_decision"
    ] = "approved"

    approved_fuzzy_matches[
        "approval_method"
    ] = "manual_review"

    return pd.concat(
        [
            exact_matches,
            approved_fuzzy_matches,
        ],
        ignore_index=True,
        sort=False,
    )
