"""Validate master-project build outputs."""

import pandas as pd


def validate_master_outputs(
    grouped_records: pd.DataFrame,
    project_master: pd.DataFrame,
    source_map: pd.DataFrame,
) -> None:
    """Validate uniqueness, coverage, and source integrity."""

    if project_master.empty:
        raise ValueError("Project master contains no rows.")

    if project_master["master_project_id"].duplicated().any():
        raise ValueError(
            "Duplicate master project IDs were found."
        )

    if project_master["match_group_id"].duplicated().any():
        raise ValueError(
            "A match group appears more than once in the master."
        )

    if project_master["master_project_name"].isna().any():
        raise ValueError(
            "One or more master project names are missing."
        )

    if len(source_map) != len(grouped_records):
        raise ValueError(
            "Source-map row count does not equal source records."
        )

    if source_map["source_record_key"].duplicated().any():
        raise ValueError(
            "Duplicate source identities were found in the map."
        )

    missing_master_ids = source_map[
        "master_project_id"
    ].isna()

    if missing_master_ids.any():
        raise ValueError(
            "One or more source records lack a master project ID."
        )

    unknown_master_ids = set(
        source_map["master_project_id"]
    ).difference(project_master["master_project_id"])

    if unknown_master_ids:
        raise ValueError(
            "The source map refers to unknown master projects."
        )

    source_counts = source_map.groupby(
        [
            "master_project_id",
            "source_dataset",
        ]
    ).size()
    same_source_conflicts = source_counts[
        source_counts > 1
    ]

    if not same_source_conflicts.empty:
        raise ValueError(
            "A master project contains multiple identities "
            "from the same source:\n"
            + same_source_conflicts.to_string()
        )

    expected_group_count = grouped_records[
        "match_group_id"
    ].nunique()

    if len(project_master) != expected_group_count:
        raise ValueError(
            "Master-project count does not equal match groups."
        )
