"""Orchestration for building the processed TfNSW project timeline."""

import pandas as pd

from .config import (
    EXPECTED_PROJECT_GROUPS,
    OUTPUT_FILE,
    REQUIRED_SHAPE_COLUMNS,
    REQUIRED_WORD_COLUMNS,
    SHAPES_INPUT_FILE,
    WORDS_INPUT_FILE,
)
from .project_rows import (
    add_vertical_centers,
    extract_project_groups,
    reconstruct_project_rows,
)
from .timeline_shapes import (
    clean_timeline_shapes,
    convert_shapes_to_timeline,
    match_shapes_to_projects,
)
from .validation import validate_input, validate_output


def run_pipeline() -> pd.DataFrame:
    """Build, validate, save, and return the processed timeline."""

    words = pd.read_csv(WORDS_INPUT_FILE)
    shapes = pd.read_csv(SHAPES_INPUT_FILE)
    validate_input(words, REQUIRED_WORD_COLUMNS, "Words extract")
    validate_input(shapes, REQUIRED_SHAPE_COLUMNS, "Shapes extract")

    words = add_vertical_centers(words)
    project_groups = extract_project_groups(words)
    if len(project_groups) != EXPECTED_PROJECT_GROUPS:
        raise ValueError(
            f"Expected {EXPECTED_PROJECT_GROUPS} project groups, "
            f"but found {len(project_groups)}."
        )

    project_rows = reconstruct_project_rows(words, project_groups)
    cleaned_shapes = clean_timeline_shapes(shapes)
    matched_shapes = match_shapes_to_projects(cleaned_shapes, project_rows)
    project_timeline = convert_shapes_to_timeline(matched_shapes)
    validate_output(project_rows, project_timeline)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    project_timeline.to_csv(OUTPUT_FILE, index=False)

    """ print("Project groups:", len(project_groups))
    print("Project rows:", len(project_rows))
    print("Cleaned shapes:", len(cleaned_shapes))
    print("Matched shapes:", len(matched_shapes))
    print("Final timeline segments:", len(project_timeline))
    print("Projects represented:", project_timeline["tfnsw_project_id"].nunique())
    print("\nValidation passed.")
    print("\nFile created:") """
    
    print(OUTPUT_FILE)
    return project_timeline
