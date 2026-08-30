from pathlib import Path

import pdfplumber

from .config import (
    BUDGET_SOURCES,
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

    print(
        "\nAll Budget Paper sources passed validation."
    )


def main() -> None:
    """Run validation without starting extraction."""

    validate_sources()


if __name__ == "__main__":
    main()