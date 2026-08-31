"""Load and standardise projects from each processed source."""

from pathlib import Path

import pandas as pd

from .config import SOURCE_DATASETS


STANDARD_COLUMNS = (
    "source_dataset",
    "source_project_id",
    "source_project_name",
    "source_agency",
    "source_location",
    "source_group",
    "source_url",
    "source_record_count",
)

REQUIRED_CONFIG_KEYS = {
    "file_path",
    "id_column",
    "name_column",
    "agency_column",
    "location_column",
    "group_column",
    "url_column",
    "year_column",
}


def validate_source_config(
    source_name: str,
    source_config: dict,
) -> None:
    """Validate the configuration for one project source."""

    missing_keys = REQUIRED_CONFIG_KEYS.difference(
        source_config
    )

    if missing_keys:
        raise ValueError(
            f"{source_name} configuration is missing: "
            f"{', '.join(sorted(missing_keys))}"
        )

    file_path = source_config["file_path"]

    if not isinstance(file_path, Path):
        raise TypeError(
            f"{source_name} file_path must be a Path."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"{source_name} file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"{source_name} path is not a file: "
            f"{file_path}"
        )

    if file_path.suffix.lower() != ".csv":
        raise ValueError(
            f"{source_name} source is not a CSV: "
            f"{file_path}"
        )


def validate_source_data(
    source_name: str,
    source_config: dict,
    data: pd.DataFrame,
) -> None:
    """Validate the columns and project identifiers in one source."""

    configured_columns = {
        source_config["id_column"],
        source_config["name_column"],
        source_config["agency_column"],
        source_config["location_column"],
        source_config["group_column"],
        source_config["url_column"],
        source_config["year_column"],
    }

    required_columns = {
        column
        for column in configured_columns
        if column is not None
    }

    missing_columns = required_columns.difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            f"{source_name} is missing required columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    if data.empty:
        raise ValueError(
            f"{source_name} contains no records."
        )

    id_column = source_config["id_column"]
    name_column = source_config["name_column"]

    missing_ids = (
        data[id_column].isna()
        | data[id_column]
        .astype(str)
        .str.strip()
        .eq("")
    )

    if missing_ids.any():
        raise ValueError(
            f"{source_name} contains "
            f"{missing_ids.sum()} records with "
            f"missing project IDs."
        )

    missing_names = (
        data[name_column].isna()
        | data[name_column]
        .astype(str)
        .str.strip()
        .eq("")
    )

    if missing_names.any():
        raise ValueError(
            f"{source_name} contains "
            f"{missing_names.sum()} records with "
            f"missing project names."
        )


def get_optional_column(
    data: pd.DataFrame,
    column_name: str | None,
) -> pd.Series:
    """Return a configured column or an empty string series."""

    if column_name is None:
        return pd.Series(
            "",
            index=data.index,
            dtype="string",
        )

    return (
        data[column_name]
        .astype("string")
        .str.strip()
    )


def load_source_projects(
    source_name: str,
    source_config: dict,
) -> pd.DataFrame:
    """Load one distinct project record per source project ID."""

    validate_source_config(
        source_name=source_name,
        source_config=source_config,
    )

    data = pd.read_csv(
        source_config["file_path"],
        keep_default_na=False,
    )

    validate_source_data(
        source_name=source_name,
        source_config=source_config,
        data=data,
    )

    id_column = source_config["id_column"]
    name_column = source_config["name_column"]
    year_column = source_config["year_column"]

    source_record_counts = (
        data.groupby(id_column)
        .size()
        .rename("source_record_count")
    )

    # Budget projects have multiple annual snapshots.
    # Sorting makes the latest budget year the retained record.
    if year_column is not None:
        data = data.sort_values(
            by=[
                id_column,
                year_column,
            ]
        )

    projects = data.drop_duplicates(
        subset=[id_column],
        keep="last",
    ).copy()

    projects["source_record_count"] = (
        projects[id_column].map(
            source_record_counts
        )
    )

    standardised = pd.DataFrame(
        {
            "source_dataset": source_name,
            "source_project_id": (
                projects[id_column]
                .astype("string")
                .str.strip()
            ),
            "source_project_name": (
                projects[name_column]
                .astype("string")
                .str.strip()
            ),
            "source_agency": get_optional_column(
                projects,
                source_config["agency_column"],
            ),
            "source_location": get_optional_column(
                projects,
                source_config["location_column"],
            ),
            "source_group": get_optional_column(
                projects,
                source_config["group_column"],
            ),
            "source_url": get_optional_column(
                projects,
                source_config["url_column"],
            ),
            "source_record_count": projects[
                "source_record_count"
            ],
        }
    )

    return standardised[
        list(STANDARD_COLUMNS)
    ].reset_index(drop=True)


def load_all_source_projects() -> pd.DataFrame:
    """Load and combine distinct projects from all sources."""

    if not SOURCE_DATASETS:
        raise ValueError(
            "No source datasets are configured."
        )

    source_projects = []

    for source_name, source_config in (
        SOURCE_DATASETS.items()
    ):
        projects = load_source_projects(
            source_name=source_name,
            source_config=source_config,
        )

        source_projects.append(projects)

    combined = pd.concat(
        source_projects,
        ignore_index=True,
    )

    duplicate_source_ids = combined.duplicated(
        subset=[
            "source_dataset",
            "source_project_id",
        ],
        keep=False,
    )

    if duplicate_source_ids.any():
        duplicates = combined.loc[
            duplicate_source_ids,
            [
                "source_dataset",
                "source_project_id",
                "source_project_name",
            ],
        ]

        raise ValueError(
            "Duplicate source project identities found:\n"
            + duplicates.to_string(index=False)
        )

    return combined[
        list(STANDARD_COLUMNS)
    ]