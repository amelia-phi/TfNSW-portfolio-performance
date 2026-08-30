"""Configuration for the Infrastructure Budget NSW extractor."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "budget_statements"
)

INTERIM_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "budget_transport_words_raw.csv"
)

BUDGET_SOURCES = {
    "2024-25": {
        "file_path": (
            RAW_DATA_DIR
            / "bp3-infrastructure-statement-2024-25.pdf"
        ),
        "transport_sections": {
            "general_government": list(range(141, 149)),
            "public_non_financial_corporation": list(
                range(155, 157)
            ),
        },
    },
    "2025-26": {
        "file_path": (
            RAW_DATA_DIR
            / "bp3-infrastructure-statement-nsw-budget-2025-26.pdf"
        ),
        "transport_sections": {
            "general_government": list(range(152, 160)),
            "public_non_financial_corporation": list(
                range(168, 170)
            ),
        },
    },
    "2026-27": {
        "file_path": (
            RAW_DATA_DIR
            / "bp3-infrastructure-statement-nsw-budget-2026-27.pdf"
        ),
        "transport_sections": {
            "general_government": list(range(149, 156)),
            "public_non_financial_corporation": list(
                range(164, 166)
            ),
        },
    },
}


EXPECTED_PAGE_HEADERS = {
    "Transport",
    "Project Description",
    "Location",
    "Start",
    "Complete",
    "Estimated",
    "Allocation",
}


MINIMUM_TEXT_CHARACTERS = 100