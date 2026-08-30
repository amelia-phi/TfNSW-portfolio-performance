import pandas as pd

from .config import (
    BUDGET_SOURCES,
    INTERIM_OUTPUT_FILE,
)
from .extractor import extract_source
from .validation import (
    validate_extracted_records,
    validate_sources,
)


def run_pipeline() -> None:
    """Extract all configured Budget Paper Transport pages."""

    validate_sources()

    extracted_sources = []

    for budget_year, source_config in (
        BUDGET_SOURCES.items()
    ):
        source_data = extract_source(
            budget_year=budget_year,
            source_config=source_config,
        )

        extracted_sources.append(source_data)

        print(
            f"Extracted: {budget_year} "
            f"({len(source_data):,} words)"
        )

    combined = pd.concat(
        extracted_sources,
        ignore_index=True,
    )

    validate_extracted_records(combined)

    INTERIM_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined.to_csv(
        INTERIM_OUTPUT_FILE,
        index=False,
    )

    print(f"\nTotal extracted words: {len(combined):,}")
    print("File created:")
    print(INTERIM_OUTPUT_FILE)
