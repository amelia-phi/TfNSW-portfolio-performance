from pathlib import Path

import pandas as pd
import pdfplumber

from .config import (
    BUDGET_SOURCES,
    EXTRACTED_WORD_COLUMNS,
    EXPECTED_PAGE_HEADERS,
    MINIMUM_TEXT_CHARACTERS,
)


def validate_file(
    budget_year: str,
    file_path: Path,
) -> None:
    """Validate one configured Budget Paper PDF."""

    if budget_year not in BUDGET_SOURCES:
        raise ValueError(
            f"Unknown budget year: {budget_year}"
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Source is not a file: {file_path}"
        )

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Source is not a PDF: {file_path}"
        )

    transport_sections = BUDGET_SOURCES[
        budget_year
    ]["transport_sections"]

    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

        if total_pages == 0:
            raise ValueError(
                f"PDF contains no pages: {file_path}"
            )

        for section_name, page_numbers in (
            transport_sections.items()
        ):
            if not page_numbers:
                raise ValueError(
                    f"No pages configured for "
                    f"{budget_year} {section_name}."
                )

            for page_number in page_numbers:
                if (
                    page_number < 1
                    or page_number > total_pages
                ):
                    raise ValueError(
                        f"Page {page_number} does not exist "
                        f"in {file_path.name}. The PDF has "
                        f"{total_pages} pages."
                    )

                # Human page 1 is Python position 0.
                page = pdf.pages[page_number - 1]

                # extract_text() can return None.
                text = page.extract_text() or ""

                if (
                    len(text.strip())
                    < MINIMUM_TEXT_CHARACTERS
                ):
                    raise ValueError(
                        f"{budget_year} {section_name} "
                        f"page {page_number} contains "
                        f"insufficient text."
                    )

                normalised_text = text.casefold()

                missing_headers = [
                    header
                    for header in EXPECTED_PAGE_HEADERS
                    if header.casefold()
                    not in normalised_text
                ]

                if missing_headers:
                    raise ValueError(
                        f"{budget_year} {section_name} "
                        f"page {page_number} is missing: "
                        f"{', '.join(sorted(missing_headers))}"
                    )


def validate_sources() -> None:
    """Validate all configured Budget Paper sources."""

    if not BUDGET_SOURCES:
        raise ValueError(
            "No Budget Paper sources are configured."
        )

    for budget_year, source_config in (
        BUDGET_SOURCES.items()
    ):
        file_path = source_config["file_path"]

        validate_file(
            budget_year=budget_year,
            file_path=file_path,
        )

        print(
            f"Passed: {budget_year} "
            f"({file_path.name})"
        )


def validate_extracted_records(data: pd.DataFrame) -> None:
    """Validate the combined positioned-word extract."""

    if data.empty:
        raise ValueError(
            "The Budget Paper extraction returned no records."
        )

    missing_columns = set(EXTRACTED_WORD_COLUMNS).difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            "Extracted data is missing required columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    expected_years = set(BUDGET_SOURCES)
    extracted_years = set(
        data["budget_year"].dropna().unique()
    )

    missing_years = expected_years.difference(
        extracted_years
    )
    unexpected_years = extracted_years.difference(
        expected_years
    )

    if missing_years:
        raise ValueError(
            "No extracted records found for budget years: "
            f"{', '.join(sorted(missing_years))}"
        )

    if unexpected_years:
        raise ValueError(
            "Unexpected budget years found: "
            f"{', '.join(sorted(unexpected_years))}"
        )

    expected_pages = {
        (budget_year, section_name, page_number)
        for budget_year, source_config in BUDGET_SOURCES.items()
        for section_name, page_numbers in source_config[
            "transport_sections"
        ].items()
        for page_number in page_numbers
    }
    extracted_pages = set(
        data[
            [
                "budget_year",
                "government_sector",
                "page_number",
            ]
        ].itertuples(index=False, name=None)
    )

    missing_pages = expected_pages.difference(
        extracted_pages
    )
    unexpected_pages = extracted_pages.difference(
        expected_pages
    )

    if missing_pages:
        raise ValueError(
            "No extracted words found for configured pages: "
            f"{sorted(missing_pages)}"
        )

    if unexpected_pages:
        raise ValueError(
            "Words were extracted from unexpected pages: "
            f"{sorted(unexpected_pages)}"
        )

    empty_text = (
        data["text"].isna()
        | data["text"].astype(str).str.strip().eq("")
    )

    if empty_text.any():
        raise ValueError(
            "One or more extracted word records have no text."
        )

    invalid_page_numbers = (
        data["page_number"].isna()
        | (data["page_number"] < 1)
    )

    if invalid_page_numbers.any():
        raise ValueError(
            "One or more extracted records have an invalid "
            "page number."
        )

    invalid_coordinates = (
        (data["page_width"] <= 0)
        | (data["page_height"] <= 0)
        | (data["x0"] < 0)
        | (data["x1"] < data["x0"])
        | (data["x1"] > data["page_width"])
        | (data["top"] < 0)
        | (data["bottom"] < data["top"])
        | (data["bottom"] > data["page_height"])
    )

    if invalid_coordinates.any():
        raise ValueError(
            "One or more extracted words have invalid page "
            "coordinates."
        )

    duplicate_word_positions = data.duplicated(
        subset=[
            "budget_year",
            "government_sector",
            "page_number",
            "word_order",
        ]
    )

    if duplicate_word_positions.any():
        raise ValueError(
            "Duplicate word-order positions were found within "
            "a configured page."
        )


