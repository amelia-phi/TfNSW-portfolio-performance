"""Configuration for master-project dataset construction."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

REGISTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_register.csv"
)
TIMELINE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_timeline.csv"
)
BUDGET_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "budget_project_snapshots.csv"
)

SOURCE_RECORDS_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "project_source_records.csv"
)
MATCH_CANDIDATES_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "project_match_candidates.csv"
)
MATCH_DECISIONS_FILE = (
    PROJECT_ROOT
    / "documentation"
    / "project_matching_log.csv"
)
MASTER_PROJECT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_master.csv"
)
SOURCE_MAP_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_source_map.csv"
)

SOURCE_DATASETS = {
    "project_register": {
        "file_path": REGISTER_FILE,
        "id_column": "project_id",
        "name_column": "project_name",
        "agency_column": None,
        "location_column": None,
        "group_column": "pipeline_category",
        "url_column": "project_url",
        "year_column": None,
    },
    "project_timeline": {
        "file_path": TIMELINE_FILE,
        "id_column": "tfnsw_project_id",
        "name_column": "project_name",
        "agency_column": None,
        "location_column": None,
        "group_column": "project_group",
        "url_column": None,
        "year_column": None,
    },
    "budget_paper": {
        "file_path": BUDGET_FILE,
        "id_column": "project_id",
        "name_column": "project_name",
        "agency_column": "agency_group",
        "location_column": "location",
        "group_column": "program_group",
        "url_column": None,
        "year_column": "budget_year",
    },
}

# Prefer the register name, followed by the timeline and Budget Paper.
MASTER_NAME_PRIORITY = (
    "project_register",
    "project_timeline",
    "budget_paper",
)

# Similarity generates review candidates; it never approves them.
MINIMUM_CANDIDATE_SCORE = 0.70
