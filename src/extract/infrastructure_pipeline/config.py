"""Configuration for the Infrastructure NSW workbook extractor."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "infrastructure_pipeline"
    / "Pipeline-28-08-2026.xlsx"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "infrastructure_pipeline_transport_raw.csv"
)

HEADER_ROW = 1
TARGET_SECTOR = "Transport"

SHEET_CONFIG = (
    {"sheet_name": "Pipeline", "lifecycle": "Pipeline"},
    {"sheet_name": "In Planning", "lifecycle": "In Planning"},
)

EXPECTED_RECORDS_BY_LIFECYCLE = {
    "Pipeline": 27,
    "In Planning": 72,
}
EXPECTED_TOTAL_RECORDS = 99

EXPECTED_OUTPUT_COLUMNS = (
    "Sector",
    "Project name",
    "Estimated Value",
    "Procurement Strategy",
    "Current Phase",
    "Procurement Start Date (est.)",
    "Procurement End Date (est.)",
    "Construction Start Date (est.)",
    "Construction End Date (est.)",
    "Project Link",
    "Source Lifecycle",
)

EXTRACTED_WORD_COLUMNS = [
    "budget_year",
    "government_sector",
    "source_file",
    "page_number",
    "page_width",
    "page_height",
    "word_order",
    "text",
    "x0",
    "x1",
    "top",
    "bottom",
]
