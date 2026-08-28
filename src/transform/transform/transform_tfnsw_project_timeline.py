from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
        "stage_name": (
            "Concept design and/or environmental assessment"
        ),
        "timing_status": "Confirmed",
    },
    "#BFDCF5": {
        "stage_name": (
            "Concept design and/or environmental assessment"
        ),
        "timing_status": "To be confirmed",
    },
    "#EC7C0E": {
        "stage_name": (
            "Detailed or reference design procurement"
        ),
        "timing_status": "Confirmed",
    },
    "#FACEA4": {
        "stage_name": (
            "Detailed or reference design procurement"
        ),
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


QUARTERS = [
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
]


def validate_input(data, required_columns, dataset_name):
    """Check that an extracted dataset is suitable."""

    missing_columns = required_columns.difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    if data.empty:
        raise ValueError(
            f"{dataset_name} contains no records."
        )

    expected_pages = set(range(1, 10))

    actual_pages = set(
        data["page_number"].unique()
    )

    if actual_pages != expected_pages:
        raise ValueError(
            f"{dataset_name} does not contain pages 1 to 9."
        )


def main():
    """Build the TfNSW project timeline dataset."""

    words = pd.read_csv(WORDS_INPUT_FILE)
    shapes = pd.read_csv(SHAPES_INPUT_FILE)

    validate_input(
        words,
        REQUIRED_WORD_COLUMNS,
        "Words extract",
    )

    validate_input(
        shapes,
        REQUIRED_SHAPE_COLUMNS,
        "Shapes extract",
    )

    timeline_candidates = shapes[
        shapes["is_timeline_candidate"]
    ]

    print("Words:", len(words))
    print("Shapes:", len(shapes))
    print(
        "Initial timeline candidates:",
        len(timeline_candidates),
    )
    print("Input validation passed.")


if __name__ == "__main__":
    main()