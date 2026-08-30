"""Orchestration for Budget Paper project snapshots."""

import pandas as pd

from .config import (
    FINAL_COLUMN_ORDER,
    INPUT_FILE,
    OUTPUT_FILE,
    TOTALS_AUDIT_FILE,
)
from .line_builder import build_visual_lines
from .project_rows import reconstruct_rows
from .transformations import transform_projects
from .validation import (
    validate_allocation_totals,
    validate_input,
    validate_output,
)


def run_pipeline() -> pd.DataFrame:
    """Reconstruct, validate, save, and return budget project snapshots."""

    words = pd.read_csv(INPUT_FILE, keep_default_na=False)
    validate_input(words)

    visual_lines = build_visual_lines(words)
    project_rows, total_rows = reconstruct_rows(visual_lines)
    snapshots = transform_projects(project_rows)
    validate_output(snapshots)
    validate_allocation_totals(snapshots, total_rows)
    snapshots = snapshots[list(FINAL_COLUMN_ORDER)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    snapshots.to_csv(OUTPUT_FILE, index=False)

    TOTALS_AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    total_rows.to_csv(TOTALS_AUDIT_FILE, index=False)

    print(f"Input words: {len(words):,}")
    print(f"Reconstructed visual lines: {len(visual_lines):,}")
    print(f"Project snapshots: {len(snapshots):,}")
    print(f"Published total rows retained: {len(total_rows):,}")
    print("Output file:", OUTPUT_FILE)
    print("Totals audit:", TOTALS_AUDIT_FILE)
    return snapshots
