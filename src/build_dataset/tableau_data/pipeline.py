"""Build and publish Tableau-ready analytical datasets."""

from pathlib import Path
import shutil

import pandas as pd

from .config import (
    PROJECT_MASTER_FILE,
    PROJECT_SOURCE_MAP_FILE,
    TABLEAU_DATASETS,
    TABLEAU_PROJECT_MASTER_FILE,
)
from .enrichment import attach_master_project
from .validation import validate_tableau_dataset


def read_csv(file_path: Path) -> pd.DataFrame:
    """Read a required CSV without converting text to missing values."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    return pd.read_csv(
        file_path,
        keep_default_na=False,
    )


def write_csv(
    data: pd.DataFrame,
    file_path: Path,
) -> None:
    """Create the output folder and write a CSV."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    data.to_csv(
        file_path,
        index=False,
    )


def run_pipeline() -> dict[str, pd.DataFrame]:
    """Enrich, validate, and publish all Tableau datasets."""

    project_master = read_csv(
        PROJECT_MASTER_FILE
    )
    source_map = read_csv(
        PROJECT_SOURCE_MAP_FILE
    )
    outputs = {}

    for dataset_name, dataset_config in (
        TABLEAU_DATASETS.items()
    ):
        source_data = read_csv(
            dataset_config["input_file"]
        )
        tableau_data = attach_master_project(
            data=source_data,
            source_map=source_map,
            project_master=project_master,
            source_dataset=(
                dataset_config["source_dataset"]
            ),
            id_column=dataset_config["id_column"],
        )
        validate_tableau_dataset(
            source_data=source_data,
            tableau_data=tableau_data,
            project_master=project_master,
            dataset_name=dataset_name,
            row_id_column=(
                dataset_config["row_id_column"]
            ),
        )
        write_csv(
            tableau_data,
            dataset_config["output_file"],
        )
        outputs[dataset_name] = tableau_data

        print(
            f"{dataset_name}: "
            f"{len(tableau_data)} rows, "
            "0 missing master IDs"
        )

    TABLEAU_PROJECT_MASTER_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.copyfile(
        PROJECT_MASTER_FILE,
        TABLEAU_PROJECT_MASTER_FILE,
    )
    outputs["project_master"] = project_master

    print(
        "project_master:",
        len(project_master),
        "rows",
    )
    print(
        "\nTableau extracts:",
        TABLEAU_PROJECT_MASTER_FILE.parent,
    )

    return outputs
