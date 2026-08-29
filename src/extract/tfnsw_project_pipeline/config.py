"""Configuration for extracting the TfNSW projects pipeline PDF."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "tfnsw_pipeline"
    / "tfnsw-infrastructure-projects-pipeline-july-2026.pdf"
)
WORDS_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_words.csv"
)
SHAPES_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_shapes.csv"
)

WORD_COLUMNS = (
    "page_number",
    "page_width",
    "page_height",
    "text",
    "x0",
    "x1",
    "top",
    "bottom",
)

SHAPE_COLUMNS = (
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
    "is_filled",
    "is_stroked",
    "fill_color_rgb",
    "fill_color_hex",
    "stroke_color_rgb",
    "is_timeline_candidate",
)

MIN_TIMELINE_WIDTH = 3
MIN_TIMELINE_HEIGHT = 5
MAX_TIMELINE_HEIGHT = 10

EXPECTED_PAGES = 9
EXPECTED_WORDS = 1491
EXPECTED_SHAPES = 4336
EXPECTED_TIMELINE_CANDIDATES = 396
