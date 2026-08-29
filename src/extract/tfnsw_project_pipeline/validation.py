"""Validation rules for the TfNSW project-pipeline PDF extraction."""

from pathlib import Path

import pandas as pd

from .config import (
    EXPECTED_PAGES,
    EXPECTED_SHAPES,
    EXPECTED_TIMELINE_CANDIDATES,
    EXPECTED_WORDS,
)


def validate_source(input_file: Path) -> None:
    """Confirm that the expected projects pipeline PDF exists."""

    if not input_file.exists():
        raise FileNotFoundError(f"Projects pipeline PDF not found: {input_file}")
    if input_file.suffix.lower() != ".pdf":
        raise ValueError("Projects pipeline source is not a PDF.")


def validate_extraction(
    words_data: pd.DataFrame,
    shapes_data: pd.DataFrame,
) -> None:
    """Confirm extracted counts and page coverage before saving."""

    if words_data.empty:
        raise ValueError("No words were extracted from the projects PDF.")
    if shapes_data.empty:
        raise ValueError("No shapes were extracted from the projects PDF.")

    if words_data["page_number"].nunique() != EXPECTED_PAGES:
        raise ValueError(f"Expected words from {EXPECTED_PAGES} PDF pages.")
    if shapes_data["page_number"].nunique() != EXPECTED_PAGES:
        raise ValueError(f"Expected shapes from {EXPECTED_PAGES} PDF pages.")
    if len(words_data) != EXPECTED_WORDS:
        raise ValueError(
            f"Expected {EXPECTED_WORDS} words, but found {len(words_data)}."
        )
    if len(shapes_data) != EXPECTED_SHAPES:
        raise ValueError(
            f"Expected {EXPECTED_SHAPES} shapes, but found {len(shapes_data)}."
        )

    candidate_count = int(shapes_data["is_timeline_candidate"].sum())
    if candidate_count != EXPECTED_TIMELINE_CANDIDATES:
        raise ValueError(
            f"Expected {EXPECTED_TIMELINE_CANDIDATES} timeline candidates, "
            f"but found {candidate_count}."
        )
