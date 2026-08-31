"""Orchestrate construction of the master-project datasets."""

from pathlib import Path

import pandas as pd

from .candidates import generate_match_candidates
from .config import (
    MASTER_PROJECT_FILE,
    MATCH_CANDIDATES_FILE,
    MATCH_DECISIONS_FILE,
    SOURCE_MAP_FILE,
    SOURCE_RECORDS_FILE,
)
from .decisions import (
    create_decision_template,
    select_accepted_matches,
    synchronise_decisions,
)
from .grouping import assign_match_groups
from .master import (
    build_project_master,
    build_project_source_map,
)
from .normalisation import normalise_source_projects
from .sources import load_all_source_projects
from .validation import validate_master_outputs


def read_or_create_decisions(
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Create the decision log or preserve its reviewed entries."""

    template = create_decision_template(candidates)

    if not MATCH_DECISIONS_FILE.exists():
        return template

    existing = pd.read_csv(
        MATCH_DECISIONS_FILE,
        keep_default_na=False,
    )

    return synchronise_decisions(
        template=template,
        existing=existing,
        candidates=candidates,
    )


def write_csv(
    data: pd.DataFrame,
    file_path: Path,
) -> None:
    """Create the destination directory and write a CSV."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    data.to_csv(
        file_path,
        index=False,
    )


def run_pipeline() -> dict[str, pd.DataFrame]:
    """Build, validate, and publish master-project datasets."""

    source_records = normalise_source_projects(
        load_all_source_projects()
    )
    candidates = generate_match_candidates(
        source_records
    )
    decisions = read_or_create_decisions(
        candidates
    )
    accepted_matches = select_accepted_matches(
        candidates,
        decisions,
    )
    grouped_records = assign_match_groups(
        source_records,
        accepted_matches,
    )
    project_master = build_project_master(
        grouped_records
    )
    source_map = build_project_source_map(
        grouped_records,
        project_master,
    )

    validate_master_outputs(
        grouped_records=grouped_records,
        project_master=project_master,
        source_map=source_map,
    )

    write_csv(source_records, SOURCE_RECORDS_FILE)
    write_csv(candidates, MATCH_CANDIDATES_FILE)
    write_csv(decisions, MATCH_DECISIONS_FILE)
    write_csv(project_master, MASTER_PROJECT_FILE)
    write_csv(source_map, SOURCE_MAP_FILE)

    decision_counts = decisions[
        "decision"
    ].value_counts()

    print("Source identities:", len(source_records))
    print("Match candidates:", len(candidates))
    print("Accepted links:", len(accepted_matches))
    print("Master projects:", len(project_master))
    print("Source-map rows:", len(source_map))
    print("\nFuzzy review decisions:")
    print(decision_counts.to_string())
    print("\nMaster file:", MASTER_PROJECT_FILE)
    print("Source map:", SOURCE_MAP_FILE)
    print("Review log:", MATCH_DECISIONS_FILE)

    return {
        "source_records": source_records,
        "candidates": candidates,
        "decisions": decisions,
        "accepted_matches": accepted_matches,
        "grouped_records": grouped_records,
        "project_master": project_master,
        "source_map": source_map,
    }
