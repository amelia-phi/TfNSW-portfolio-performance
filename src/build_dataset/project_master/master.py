"""Build the master-project table and source-identity map."""

import pandas as pd

from .config import MASTER_NAME_PRIORITY


MASTER_COLUMNS = [
    "master_project_id",
    "master_project_name",
    "canonical_source_dataset",
    "canonical_source_project_id",
    "match_group_id",
    "source_record_count",
    "source_dataset_count",
    "source_datasets",
    "has_cross_source_match",
]


SOURCE_MAP_COLUMNS = [
    "master_project_id",
    "match_group_id",
    "source_record_key",
    "source_dataset",
    "source_project_id",
    "source_project_name",
    "normalised_project_name",
    "source_agency",
    "source_location",
    "source_group",
    "source_url",
    "source_record_count",
    "match_group_size",
    "has_cross_source_match",
]


def select_canonical_records(
    grouped_records: pd.DataFrame,
) -> pd.DataFrame:
    """Select the preferred naming record for every group."""

    required_columns = {
        "match_group_id",
        "source_dataset",
        "source_project_id",
        "source_project_name",
    }
    missing_columns = required_columns.difference(
        grouped_records.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing grouped-record columns: "
            + ", ".join(sorted(missing_columns))
        )

    source_priority = {
        source_name: priority
        for priority, source_name in enumerate(
            MASTER_NAME_PRIORITY,
            start=1,
        )
    }
    unknown_sources = set(
        grouped_records["source_dataset"].unique()
    ).difference(source_priority)

    if unknown_sources:
        raise ValueError(
            "Sources missing from master-name priority: "
            + ", ".join(sorted(unknown_sources))
        )

    ranked_records = grouped_records.copy()
    ranked_records["_source_priority"] = (
        ranked_records["source_dataset"].map(
            source_priority
        )
    )
    ranked_records = ranked_records.sort_values(
        by=[
            "match_group_id",
            "_source_priority",
            "source_project_id",
        ]
    )

    return (
        ranked_records.drop_duplicates(
            subset=["match_group_id"],
            keep="first",
        )
        .drop(columns=["_source_priority"])
        .copy()
    )


def build_project_master(
    grouped_records: pd.DataFrame,
) -> pd.DataFrame:
    """Build one canonical record per matched project group."""

    canonical_records = select_canonical_records(
        grouped_records
    )
    group_statistics = (
        grouped_records.groupby(
            "match_group_id",
            as_index=False,
        )
        .agg(
            source_record_count=(
                "source_record_key",
                "size",
            ),
            source_dataset_count=(
                "source_dataset",
                "nunique",
            ),
            source_datasets=(
                "source_dataset",
                lambda values: "; ".join(
                    sorted(set(values))
                ),
            ),
        )
    )

    master = canonical_records[
        [
            "match_group_id",
            "source_dataset",
            "source_project_id",
            "source_project_name",
        ]
    ].rename(
        columns={
            "source_dataset": (
                "canonical_source_dataset"
            ),
            "source_project_id": (
                "canonical_source_project_id"
            ),
            "source_project_name": (
                "master_project_name"
            ),
        }
    )
    master = master.merge(
        group_statistics,
        on="match_group_id",
        how="left",
        validate="one_to_one",
    )
    master = master.sort_values(
        "match_group_id"
    ).reset_index(drop=True)
    master.insert(
        0,
        "master_project_id",
        [
            f"MASTER-{number:04d}"
            for number in range(
                1,
                len(master) + 1,
            )
        ],
    )
    master["has_cross_source_match"] = (
        master["source_dataset_count"] > 1
    )

    return master[MASTER_COLUMNS]


def build_project_source_map(
    grouped_records: pd.DataFrame,
    project_master: pd.DataFrame,
) -> pd.DataFrame:
    """Map every source project identity to a master project."""

    master_keys = project_master[
        [
            "master_project_id",
            "match_group_id",
        ]
    ]
    source_map = grouped_records.merge(
        master_keys,
        on="match_group_id",
        how="left",
        validate="many_to_one",
    )

    return (
        source_map[SOURCE_MAP_COLUMNS]
        .sort_values(
            by=[
                "master_project_id",
                "source_dataset",
                "source_project_id",
            ]
        )
        .reset_index(drop=True)
    )
