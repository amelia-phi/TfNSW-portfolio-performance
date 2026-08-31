"""Validate Tableau-ready analytical datasets."""

import pandas as pd


def validate_tableau_dataset(
    source_data: pd.DataFrame,
    tableau_data: pd.DataFrame,
    project_master: pd.DataFrame,
    dataset_name: str,
    row_id_column: str,
) -> None:
    """Confirm that enrichment preserves rows and valid identities."""

    if len(tableau_data) != len(source_data):
        raise ValueError(
            f"{dataset_name} row count changed from "
            f"{len(source_data)} to {len(tableau_data)}."
        )

    if row_id_column not in tableau_data.columns:
        raise ValueError(
            f"{dataset_name} is missing {row_id_column}."
        )

    if tableau_data[row_id_column].duplicated().any():
        raise ValueError(
            f"{dataset_name} contains duplicate "
            f"{row_id_column} values."
        )

    missing_master_ids = tableau_data[
        "master_project_id"
    ].isna()

    if missing_master_ids.any():
        raise ValueError(
            f"{dataset_name} contains "
            f"{missing_master_ids.sum()} rows without "
            "a master project ID."
        )

    missing_master_names = tableau_data[
        "master_project_name"
    ].isna()

    if missing_master_names.any():
        raise ValueError(
            f"{dataset_name} contains "
            f"{missing_master_names.sum()} rows without "
            "a master project name."
        )

    unknown_master_ids = set(
        tableau_data["master_project_id"]
    ).difference(project_master["master_project_id"])

    if unknown_master_ids:
        raise ValueError(
            f"{dataset_name} contains unknown "
            "master project IDs."
        )
