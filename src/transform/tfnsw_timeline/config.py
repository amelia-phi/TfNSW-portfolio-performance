"""Configuration for the TfNSW project timeline transformation."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

WORDS_INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_words.csv"
)

SHAPES_INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_shapes.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_timeline.csv"
)

REQUIRED_WORD_COLUMNS = {
    "page_number",
    "text",
    "x0",
    "x1",
    "top",
    "bottom",
}

REQUIRED_SHAPE_COLUMNS = {
    "page_number",
    "page_width",
    "page_height",
    "shape_type",
    "x0",
    "x1",
    "top",
    "bottom",
    "width",
    "height",
    "fill_color_hex",
    "is_timeline_candidate",
}

STAGE_COLOR_MAP = {
    "#20A8E1": {
        "stage_name": "Concept design and/or environmental assessment",
        "timing_status": "Confirmed",
    },
    "#BFDCF5": {
        "stage_name": "Concept design and/or environmental assessment",
        "timing_status": "To be confirmed",
    },
    "#EC7C0E": {
        "stage_name": "Detailed or reference design procurement",
        "timing_status": "Confirmed",
    },
    "#FACEA4": {
        "stage_name": "Detailed or reference design procurement",
        "timing_status": "To be confirmed",
    },
    "#7BAE27": {
        "stage_name": "Detailed or reference design",
        "timing_status": "Confirmed",
    },
    "#D0DDAD": {
        "stage_name": "Detailed or reference design",
        "timing_status": "To be confirmed",
    },
    "#DD0030": {
        "stage_name": "Construction procurement",
        "timing_status": "Confirmed",
    },
    "#F3AEA3": {
        "stage_name": "Construction procurement",
        "timing_status": "To be confirmed",
    },
    "#173077": {
        "stage_name": "Construction and commissioning",
        "timing_status": "Confirmed",
    },
    "#9C9DC5": {
        "stage_name": "Construction and commissioning",
        "timing_status": "To be confirmed",
    },
    "#33383D": {
        "stage_name": "Rolling program",
        "timing_status": "Confirmed",
    },
    "#C3AAD2": {
        "stage_name": "Project staging not yet available",
        "timing_status": "Not available",
    },
}

QUARTERS = (
    "Q3 2026",
    "Q4 2026",
    "Q1 2027",
    "Q2 2027",
    "Q3 2027",
    "Q4 2027",
    "Q1 2028",
    "Q2 2028",
    "Q3 2028",
    "Q4 2028",
    "Q1 2029",
    "Q2 2029",
    "Q3 2029",
    "Q4 2029",
    "Q1 2030",
    "Q2 2030",
)

TIMELINE_START_X = 162.962924
QUARTER_WIDTH = 25.891305
ROW_MATCH_TOLERANCE = 4.0

EXPECTED_PAGES = set(range(1, 10))
EXPECTED_PROJECT_GROUPS = 22
EXPECTED_PROJECTS = 123
EXPECTED_TIMELINE_SEGMENTS = 225

OUTPUT_COLUMNS = (
    "timeline_id",
    "tfnsw_project_id",
    "project_name",
    "project_group",
    "estimated_value_code",
    "delivery_type",
    "stage_name",
    "timing_status",
    "start_quarter",
    "end_quarter",
    "start_quarter_index",
    "end_quarter_index",
    "fill_color_hex",
    "source_page",
    "source_shape_type",
    "source_x0",
    "source_x1",
)
