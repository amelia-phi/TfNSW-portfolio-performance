"""Attach master-project identities to analytical datasets."""

import pandas as pd


MASTER_COLUMNS = [
    "master_project_id",
    "master_project_name",
]


def normalise_identifier(
    values: pd.Series,
) -> pd.Series:
    """Standardise identifiers without changing their meaning."""

    return (
        values.astype("string")
        .str.strip()
    )


def build_source_mapping(
    source_map: pd.DataFrame,
    source_dataset: str,
) -> pd.DataFrame:
    """Return one source-ID-to-master-ID mapping."""

    required_columns = {
        "source_dataset",
        "source_project_id",
        "master_project_id",
    }
    missing_columns = required_columns.difference(
        source_map.columns
    )

    if missing_columns:
        raise ValueError(
            "Source map is missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    mapping = source_map.loc[
        source_map["source_dataset"]
        == source_dataset,
        [
            "source_project_id",
            "master_project_id",
        ],
    ].copy()

    if mapping.empty:
        raise ValueError(
            f"No source mappings found for {source_dataset}."
        )

    mapping["source_project_id"] = (
        normalise_identifier(
            mapping["source_project_id"]
        )
    )

    duplicate_ids = mapping[
        "source_project_id"
    ].duplicated(keep=False)

    if duplicate_ids.any():
        raise ValueError(
            f"Duplicate source IDs found for {source_dataset}."
        )

    return mapping


def attach_master_project(
    data: pd.DataFrame,
    source_map: pd.DataFrame,
    project_master: pd.DataFrame,
    source_dataset: str,
    id_column: str,
) -> pd.DataFrame:
    """Attach a canonical master identity to every analytical row."""

    if id_column not in data.columns:
        raise ValueError(
            f"Input dataset is missing {id_column}."
        )

    existing_master_columns = set(
        MASTER_COLUMNS
    ).intersection(data.columns)

    if existing_master_columns:
        raise ValueError(
            "Input already contains master columns: "
            + ", ".join(sorted(existing_master_columns))
        )

    mapping = build_source_mapping(
        source_map=source_map,
        source_dataset=source_dataset,
    )
    enriched = data.copy()
    enriched[id_column] = normalise_identifier(
        enriched[id_column]
    )
    enriched = enriched.merge(
        mapping,
        left_on=id_column,
        right_on="source_project_id",
        how="left",
        validate="many_to_one",
    ).drop(
        columns=["source_project_id"]
    )

    required_master_columns = {
        "master_project_id",
        "master_project_name",
    }
    missing_master_columns = (
        required_master_columns.difference(
            project_master.columns
        )
    )

    if missing_master_columns:
        raise ValueError(
            "Project master is missing columns: "
            + ", ".join(
                sorted(missing_master_columns)
            )
        )

    master_names = project_master[
        [
            "master_project_id",
            "master_project_name",
        ]
    ].copy()
    enriched = enriched.merge(
        master_names,
        on="master_project_id",
        how="left",
        validate="many_to_one",
    )

    original_columns = [
        column
        for column in data.columns
        if column not in MASTER_COLUMNS
    ]

    return enriched[
        MASTER_COLUMNS + original_columns
    ]
