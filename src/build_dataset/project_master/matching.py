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

# validate review decision
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


# select accepted relationships
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

    accepted_matches = pd.concat(
        [
            exact_matches,
            approved_fuzzy_matches,
        ],
        ignore_index=True,
        sort=False,
    )

    return accepted_matches

# add source record keys
def add_source_record_keys(
    source_records: pd.DataFrame,
) -> pd.DataFrame:
    """Add a unique cross-source key to every source project."""

    required_columns = {
        "source_dataset",
        "source_project_id",
    }

    missing_columns = required_columns.difference(
        source_records.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing source-record columns: "
            + ", ".join(sorted(missing_columns))
        )

    result = source_records.copy()

    result["source_record_key"] = (
        result["source_dataset"]
        .astype("string")
        .str.strip()
        + "::"
        + result["source_project_id"]
        .astype("string")
        .str.strip()
    )

    blank_keys = (
        result["source_record_key"]
        .isna()
        | result["source_record_key"].eq("")
    )

    if blank_keys.any():
        raise ValueError(
            "One or more source-record keys are blank."
        )

    duplicate_keys = result[
        "source_record_key"
    ].duplicated(keep=False)

    if duplicate_keys.any():
        raise ValueError(
            "Duplicate source-record keys were found."
        )

    return result

def assign_match_groups(
    source_records: pd.DataFrame,
    accepted_matches: pd.DataFrame,
) -> pd.DataFrame:
    """Assign every source project to a connected match group."""

    records = add_source_record_keys(
        source_records
    )

    record_keys = set(
        records["source_record_key"]
    )

    # Initially, every record is its own parent.
    parent = {
        record_key: record_key
        for record_key in record_keys
    }

    def find(record_key: str) -> str:
        """Find the current root of a project group."""

        while parent[record_key] != record_key:
            parent[record_key] = parent[
                parent[record_key]
            ]

            record_key = parent[record_key]

        return record_key

    def union(
        left_key: str,
        right_key: str,
    ) -> None:
        """Connect two project groups."""

        left_root = find(left_key)
        right_root = find(right_key)

        if left_root == right_root:
            return

        # Always retain the alphabetically smaller root.
        # This makes the result deterministic.
        preferred_root = min(
            left_root,
            right_root,
        )

        other_root = max(
            left_root,
            right_root,
        )

        parent[other_root] = preferred_root

    required_match_columns = {
        "left_source_dataset",
        "left_source_project_id",
        "right_source_dataset",
        "right_source_project_id",
    }

    missing_columns = (
        required_match_columns.difference(
            accepted_matches.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "Missing accepted-match columns: "
            + ", ".join(sorted(missing_columns))
        )

    for match in accepted_matches.to_dict(
        orient="records"
    ):
        left_key = (
            f"{match['left_source_dataset']}"
            f"::{match['left_source_project_id']}"
        )

        right_key = (
            f"{match['right_source_dataset']}"
            f"::{match['right_source_project_id']}"
        )

        unknown_keys = {
            left_key,
            right_key,
        }.difference(record_keys)

        if unknown_keys:
            raise ValueError(
                "Accepted match contains unknown "
                "source-record keys: "
                + ", ".join(sorted(unknown_keys))
            )

        union(
            left_key,
            right_key,
        )

    records["match_group_root"] = (
        records["source_record_key"].map(find)
    )

    unique_roots = sorted(
        records["match_group_root"].unique()
    )

    group_id_map = {
        root: f"GROUP-{number:04d}"
        for number, root in enumerate(
            unique_roots,
            start=1,
        )
    }

    records["match_group_id"] = (
        records["match_group_root"]
        .map(group_id_map)
    )

    group_sizes = (
        records.groupby("match_group_id")
        ["source_record_key"]
        .transform("size")
    )

    records["match_group_size"] = group_sizes

    records["has_cross_source_match"] = (
        records["match_group_size"] > 1
    )

    return records