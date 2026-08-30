"""Configuration for Budget Paper project transformations."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "budget_transport_words_raw.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "budget_project_snapshots.csv"
)
TOTALS_AUDIT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "budget_transport_totals.csv"
)

REQUIRED_INPUT_COLUMNS = {
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
}

# Absolute x-coordinate boundaries are stable across the three A4 papers.
COLUMN_BOUNDARIES = {
    "project_name": (0.0, 202.5),
    "location": (202.5, 268.0),
    "start_period": (268.0, 305.0),
    "completion_period": (305.0, 355.0),
    "estimated_total_cost_000_raw": (355.0, 415.0),
    "estimated_expenditure_000_raw": (415.0, 485.0),
    "annual_allocation_000_raw": (485.0, 600.0),
}

LINE_Y_TOLERANCE = 4.0
CONTINUATION_MAX_GAP = 13.0
BODY_TOP = 90.0
# Project rows can extend to about 802 points; page footers begin above 810.
BODY_BOTTOM = 805.0

AGENCY_ALIASES = {
    "transport for nsw": "Transport for NSW",
    "transport for nsw (cont)": "Transport for NSW",
    "transport for nsw (cont.)": "Transport for NSW",
    "sydney metro": "Sydney Metro",
    (
        "office of transport safety investigations"
    ): "Office of Transport Safety Investigations",
    (
        "transport asset holding entity of new south wales"
    ): "Transport Asset Holding Entity of New South Wales",
    (
        "transport asset manager new south wales"
    ): "Transport Asset Manager New South Wales",
    (
        "transport asset manager new south wales (tam)"
    ): "Transport Asset Manager New South Wales (TAM)",
    "sydney ferries": "Sydney Ferries",
    "sydney trains": "Sydney Trains",
    "nsw trains": "NSW Trains",
}

AGENCY_GROUPS = {
    "Transport for NSW": "Transport for NSW",
    "Sydney Metro": "Sydney Metro",
    (
        "Office of Transport Safety Investigations"
    ): "Office of Transport Safety Investigations",
    (
        "Transport Asset Holding Entity of New South Wales"
    ): "Transport Asset Manager/Holding Entity NSW",
    (
        "Transport Asset Manager New South Wales"
    ): "Transport Asset Manager/Holding Entity NSW",
    (
        "Transport Asset Manager New South Wales (TAM)"
    ): "Transport Asset Manager/Holding Entity NSW",
    "Sydney Ferries": "Sydney Ferries",
    "Sydney Trains": "Sydney Trains",
    "NSW Trains": "NSW Trains",
}

WORK_CATEGORIES = {
    "major works": "Major Works",
    "minor works": "Minor Works",
    "leases": "Leases",
}

DELIVERY_STATUSES = {
    "works in progress": "Works in Progress",
    "new works": "New Works",
}

FINAL_COLUMN_ORDER = (
    "snapshot_id",
    "project_id",
    "project_match_key",
    "budget_year",
    "project_name",
    "agency",
    "agency_group",
    "government_sector",
    "work_category",
    "delivery_status",
    "program_group",
    "location",
    "start_period",
    "start_year",
    "start_disclosed",
    "completion_period",
    "completion_year",
    "completion_disclosed",
    "estimated_total_cost_000",
    "total_cost_disclosed",
    "estimated_expenditure_to_june_000",
    "expenditure_disclosed",
    "annual_allocation_000",
    "allocation_disclosed",
    "source_file",
    "source_page",
    "source_row_top",
)
