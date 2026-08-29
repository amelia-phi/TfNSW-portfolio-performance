"""Orchestration for building the processed project register."""

import pandas as pd

from .config import (
    FINAL_COLUMN_ORDER,
    INPUT_FILE,
    OUTPUT_FILE,
    VALIDATION_OUTPUT_FILE,
)
from .duplicates import (
    build_duplicate_log,
    consolidate_projects,
    identify_duplicates,
    validate_duplicates,
)
from .transformations import (
    add_project_ids,
    decode_reference_values,
    standardise_column_names,
)
from .validation import validate_input, validate_output, validate_reference_values


def run_pipeline() -> pd.DataFrame:
    """Build, validate, save, and return the processed project register."""

    data = pd.read_csv(INPUT_FILE)
    validate_input(data)

    duplicates = identify_duplicates(data)
    validate_duplicates(duplicates)
    project_register = consolidate_projects(data)
    duplicate_log = build_duplicate_log(duplicates)

    project_register = standardise_column_names(project_register)
    project_register = decode_reference_values(project_register)
    project_register = add_project_ids(project_register)
    validate_reference_values(project_register)
    validate_output(project_register)
    project_register = project_register[list(FINAL_COLUMN_ORDER)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    project_register.to_csv(OUTPUT_FILE, index=False)
    VALIDATION_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    duplicate_log.to_csv(VALIDATION_OUTPUT_FILE, index=False)

    duplicate_project_count = duplicates["Project name"].nunique()
    print(f"Input validation passed: {len(data)} records.")
    print(
        "Duplicate check passed: "
        f"{len(duplicates)} source rows across "
        f"{duplicate_project_count} project."
    )
    print(f"Final register created: {len(project_register)} unique projects.")
    print("Output file:", OUTPUT_FILE)
    print("Validation log:", VALIDATION_OUTPUT_FILE)
    return project_register
