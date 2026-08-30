from pathlib import Path

import pandas as pd
import pdfplumber
from pdfplumber.page import Page

from .config import EXTRACTED_WORD_COLUMNS


def extract_page_words(
    page: Page,
    budget_year: str,
    government_sector: str,
    source_file: Path,
    page_number: int,
) -> list[dict]:
    """Extract positioned words from one Transport page."""

    words = page.extract_words(
        x_tolerance=3,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=False,
    )

    records = []

    for word_order, word in enumerate(
        words,
        start=1,
    ):
        text = word.get("text", "")

        if not text:
            continue

        record = {
            "budget_year": budget_year,
            "government_sector": government_sector,
            "source_file": source_file.name,
            "page_number": page_number,
            "page_width": page.width,
            "page_height": page.height,
            "word_order": word_order,
            "text": text,
            "x0": word["x0"],
            "x1": word["x1"],
            "top": word["top"],
            "bottom": word["bottom"],
        }

        records.append(record)

    return records


def extract_source(
    budget_year: str,
    source_config: dict,
) -> pd.DataFrame:
    """Extract words from one Budget Paper source."""

    file_path = source_config["file_path"]
    transport_sections = source_config[
        "transport_sections"
    ]

    source_records = []

    with pdfplumber.open(file_path) as pdf:
        for government_sector, page_numbers in (
            transport_sections.items()
        ):
            for page_number in page_numbers:
                # Human page 1 is Python position 0.
                page = pdf.pages[page_number - 1]

                page_records = extract_page_words(
                    page=page,
                    budget_year=budget_year,
                    government_sector=government_sector,
                    source_file=file_path,
                    page_number=page_number,
                )

                source_records.extend(page_records)

    return pd.DataFrame(
        source_records,
        columns=EXTRACTED_WORD_COLUMNS,
    )