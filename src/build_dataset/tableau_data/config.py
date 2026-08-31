"""Configuration for Tableau-ready analytical datasets."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLEAU_EXTRACT_DIR = PROJECT_ROOT / "tableau" / "extracts"

PROJECT_MASTER_FILE = (
    PROCESSED_DIR / "project_master.csv"
)
PROJECT_SOURCE_MAP_FILE = (
    PROCESSED_DIR / "project_source_map.csv"
)
TABLEAU_PROJECT_MASTER_FILE = (
    TABLEAU_EXTRACT_DIR / "project_master.csv"
)

TABLEAU_DATASETS = {
    "project_register": {
        "input_file": (
            PROCESSED_DIR / "project_register.csv"
        ),
        "output_file": (
            TABLEAU_EXTRACT_DIR
            / "project_register.csv"
        ),
        "source_dataset": "project_register",
        "id_column": "project_id",
        "row_id_column": "project_id",
    },
    "project_timeline": {
        "input_file": (
            PROCESSED_DIR / "project_timeline.csv"
        ),
        "output_file": (
            TABLEAU_EXTRACT_DIR
            / "project_timeline.csv"
        ),
        "source_dataset": "project_timeline",
        "id_column": "tfnsw_project_id",
        "row_id_column": "timeline_id",
    },
    "budget_project_snapshots": {
        "input_file": (
            PROCESSED_DIR
            / "budget_project_snapshots.csv"
        ),
        "output_file": (
            TABLEAU_EXTRACT_DIR
            / "budget_project_snapshots.csv"
        ),
        "source_dataset": "budget_paper",
        "id_column": "project_id",
        "row_id_column": "snapshot_id",
    },
}
