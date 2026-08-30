import pandas as pd

from .config import (
    BUDGET_SOURCES,
    INTERIM_OUTPUT_FILE,
)
from .extractor import extract_source
from .validation import validate_sources


def run_pipeline() -> None:
    """Extract all configured Budget Paper Transport pages."""

    validate_sources()

    extracted_sources = []