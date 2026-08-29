"""Orchestration for extracting the TfNSW projects pipeline PDF."""

import logging
from pathlib import Path

import pandas as pd

from .config import INPUT_FILE, SHAPES_OUTPUT_FILE, WORDS_OUTPUT_FILE
from .parser import extract_pdf_content
from .validation import validate_extraction, validate_source


logging.getLogger("pdfminer").setLevel(logging.ERROR)


def _save_output(data: pd.DataFrame, output_file: Path) -> None:
    """Save one extracted dataset as CSV."""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_file, index=False)


def run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extract, validate, save, and return the project-pipeline datasets."""

    validate_source(INPUT_FILE)
    words_data, shapes_data = extract_pdf_content(INPUT_FILE)
    validate_extraction(words_data, shapes_data)

    _save_output(words_data, WORDS_OUTPUT_FILE)
    _save_output(shapes_data, SHAPES_OUTPUT_FILE)

    timeline_candidate_count = int(shapes_data["is_timeline_candidate"].sum())
    print("\nExtraction complete")
    print("Total words:", len(words_data))
    print("Total shapes:", len(shapes_data))
    print("Possible timeline shapes:", timeline_candidate_count)
    print("\nFiles created:")
    print(WORDS_OUTPUT_FILE)
    print(SHAPES_OUTPUT_FILE)
    return words_data, shapes_data
