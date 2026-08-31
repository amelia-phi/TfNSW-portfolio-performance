# where are the 3 input datasets?
# where should generated files be saved?
# which ID and name columns belong to each source?
# which is the preferred source order for selecting a master name?
# what similarity score should quantify as a review?


"""Configuration for master-project dataset construction."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# define 3 input paths
REGISTER_FILE = (PROJECT_ROOT / "data" / "processed"/"project_register.csv")
TIMELINE_FILE = (PROJECT_ROOT / "data" / "processed"/"project_timeline.csv")
BUDGET_FILE = (PROJECT_ROOT / "data" / "processed"/"budget_project_snapshots.csv")

# defined output paths
SOURCE_RECORDS_FILE = (PROJECT_ROOT / "data" / "interim" / "project_source_records.csv")
MATCH_CANDIDATES_FILE = (PROJECT_ROOT / "data" / "interim" / "project_match_candidates.csv")
MATCH_DECISIONS_FILE = (PROJECT_ROOT / "data" / "interim" / "project_match_decisions.csv")
MASTER_PROJECT_FILE = (PROJECT_ROOT / "data" / "interim" / "master_project.csv")
SOURCE_MAP_FILE = (PROJECT_ROOT / "data" / "interim" / "source_map.csv")

# create a dictionary describing the columns in each source
SOURCE_DATASETS = {
    "project_register": {
        "file_path": REGISTER_FILE,
        "id_column": "project_id",
        "name_column": "project_name",
    },
    "project_timeline": {
        "file_path": TIMELINE_FILE,
        "id_column": "tfnsw_project_id",
        "name_column": "project_name",
    },
    "budget_paper": {
        "file_path": BUDGET_FILE,
        "id_column": "project_id",
        "name_column": "project_name",
    },
}

"""master name preference - if a project appears in multiple sources, 
prefer the name from the project_register, then project_timeline, then budget plan"""
MASTER_NAME_PRIORITY = [
    "project_register",
    "project_timeline",
    "budget_paper",
]

# we use name similarity to create review candidates, NOT AUTOMATIC APPROVALS
MINIMUM_CANDIDATE_SCORE = 0.7
