"""Apply reviewed decisions to project-match candidates."""

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

# build the fuzzy-review template
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