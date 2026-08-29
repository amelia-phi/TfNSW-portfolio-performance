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


TIMELINE_START_X = 162.962924
QUARTER_WIDTH = 25.891305
ROW_MATCH_TOLERANCE = 4.0


def validate_input(
    data,
    required_columns,
    dataset_name,
):
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


def extract_project_groups(words):
    """Extract headings such as Central Coast roads."""

    group_records = []

    data_set_labels = words[
        (words["text"] == "Set")
        & (words["x0"] > 500)
    ]

    for _, label in data_set_labels.iterrows():
        page_number = label["page_number"]
        label_center = label["vertical_center"]

        group_words = words[
            (words["page_number"] == page_number)
            & (words["x0"] < 160)
            & (
                (
                    words["vertical_center"]
                    - label_center
                ).abs()
                <= 12
            )
        ].sort_values(
            by=["top", "x0"]
        )

        project_group = " ".join(
            group_words["text"].astype(str)
        )

        group_records.append(
            {
                "page_number": page_number,
                "group_center": label_center,
                "project_group": project_group,
            }
        )

    project_groups = pd.DataFrame(
        group_records
    )

    return project_groups.sort_values(
        by=["page_number", "group_center"]
    ).reset_index(drop=True)


def reconstruct_project_rows(
    words,
    project_groups,
):
    """Rebuild project records from positioned words."""

    value_anchors = words[
        words["text"]
        .astype(str)
        .str.fullmatch(
            r"\${1,6}|TBA",
            na=False,
        )
        & words["x0"].between(88, 120)
    ].sort_values(
        by=["page_number", "top"]
    )

    project_records = []

    for _, anchor in value_anchors.iterrows():
        page_number = anchor["page_number"]
        row_center = anchor["vertical_center"]

        row_words = words[
            (words["page_number"] == page_number)
            & (
                (
                    words["vertical_center"]
                    - row_center
                ).abs()
                <= 15.5
            )
        ]

        project_name_words = row_words[
            row_words["x0"] < 92
        ].sort_values(
            by=["top", "x0"]
        )

        delivery_words = row_words[
            (row_words["x0"] >= 120)
            & (row_words["x0"] < 161)
        ].sort_values(
            by=["top", "x0"]
        )

        project_name = " ".join(
            project_name_words["text"].astype(str)
        )

        delivery_type = " ".join(
            delivery_words["text"].astype(str)
        )

        # Ignore repeated table headings.
        if (
            project_name == "Project"
            and delivery_type == "Delivery type"
        ):
            continue

        earlier_groups = project_groups[
            (
                project_groups["page_number"]
                < page_number
            )
            | (
                (
                    project_groups["page_number"]
                    == page_number
                )
                & (
                    project_groups["group_center"]
                    < row_center
                )
            )
        ]

        if earlier_groups.empty:
            project_group = pd.NA
        else:
            project_group = (
                earlier_groups.iloc[-1][
                    "project_group"
                ]
            )

        project_records.append(
            {
                "project_row_id": (
                    len(project_records) + 1
                ),
                "project_name": project_name,
                "project_group": project_group,
                "estimated_value_code": (
                    anchor["text"]
                ),
                "delivery_type": delivery_type,
                "source_page": page_number,
                "row_center": row_center,
            }
        )

    return pd.DataFrame(project_records)


def clean_timeline_shapes(shapes):
    """Keep valid shapes and remove exact duplicates."""

    candidate_mask = (
        shapes["is_timeline_candidate"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    data = shapes[
        candidate_mask
        & shapes["fill_color_hex"].isin(
            STAGE_COLOR_MAP
        )
    ].copy()

    duplicate_columns = [
        "page_number",
        "shape_type",
        "x0",
        "x1",
        "top",
        "bottom",
        "fill_color_hex",
    ]

    data = data.drop_duplicates(
        subset=duplicate_columns
    )

    # Remove shapes outside the visible page.
    data = data[
        (data["x0"] >= 160)
        & (
            data["x1"]
            <= data["page_width"] + 0.01
        )
        & (data["top"] >= 0)
        & (
            data["bottom"]
            <= data["page_height"]
        )
    ].copy()

    data["shape_center"] = (
        data["top"] + data["bottom"]
    ) / 2

    return data


def match_shapes_to_projects(
    shapes,
    project_rows,
):
    """Match each shape to its nearest project row."""

    matched_records = []

    for _, shape in shapes.iterrows():
        page_projects = project_rows[
            project_rows["source_page"]
            == shape["page_number"]
        ].copy()

        if page_projects.empty:
            continue

        page_projects["match_distance"] = (
            page_projects["row_center"]
            - shape["shape_center"]
        ).abs()

        nearest_index = (
            page_projects["match_distance"]
            .idxmin()
        )

        nearest_project = page_projects.loc[
            nearest_index
        ]

        if (
            nearest_project["match_distance"]
            > ROW_MATCH_TOLERANCE
        ):
            continue

        record = shape.to_dict()

        record.update(
            {
                "project_row_id": nearest_project[
                    "project_row_id"
                ],
                "project_name": nearest_project[
                    "project_name"
                ],
                "project_group": nearest_project[
                    "project_group"
                ],
                "estimated_value_code": (
                    nearest_project[
                        "estimated_value_code"
                    ]
                ),
                "delivery_type": nearest_project[
                    "delivery_type"
                ],
                "source_page": nearest_project[
                    "source_page"
                ],
                "match_distance": nearest_project[
                    "match_distance"
                ],
            }
        )

        matched_records.append(record)

    return pd.DataFrame(matched_records)


def convert_shapes_to_timeline(
    matched_shapes,
):
    """Convert coordinates into timeline periods."""

    data = matched_shapes.copy()

    data["start_quarter_index"] = (
        (
            data["x0"] - TIMELINE_START_X
        )
        / QUARTER_WIDTH
    ).round().clip(
        lower=0,
        upper=len(QUARTERS) - 1,
    ).astype(int)

    end_boundary_index = (
        (
            data["x1"] - TIMELINE_START_X
        )
        / QUARTER_WIDTH
    ).round().clip(
        lower=1,
        upper=len(QUARTERS),
    ).astype(int)

    data["end_quarter_index"] = (
        end_boundary_index - 1
    )

    data = data[
        data["end_quarter_index"]
        >= data["start_quarter_index"]
    ].copy()

    data["stage_name"] = (
        data["fill_color_hex"].map(
            lambda color: STAGE_COLOR_MAP[
                color
            ]["stage_name"]
        )
    )

    data["timing_status"] = (
        data["fill_color_hex"].map(
            lambda color: STAGE_COLOR_MAP[
                color
            ]["timing_status"]
        )
    )

    quarter_lookup = dict(
        enumerate(QUARTERS)
    )

    data["start_quarter"] = (
        data["start_quarter_index"].map(
            quarter_lookup
        )
    )

    data["end_quarter"] = (
        data["end_quarter_index"].map(
            quarter_lookup
        )
    )

    # Remove shapes representing the same segment.
    data = data.drop_duplicates(
        subset=[
            "project_row_id",
            "fill_color_hex",
            "start_quarter_index",
            "end_quarter_index",
        ]
    )

    interval_columns = [
        "project_row_id",
        "start_quarter_index",
        "end_quarter_index",
    ]

    data["interval_key"] = list(
        data[interval_columns].itertuples(
            index=False,
            name=None,
        )
    )

    # Purple is sometimes drawn underneath another stage.
    # Keep it only when no other stage occupies the interval.
    non_purple_intervals = set(
        data.loc[
            data["fill_color_hex"] != "#C3AAD2",
            "interval_key",
        ]
    )

    data = data[
        ~(
            (data["fill_color_hex"] == "#C3AAD2")
            & data["interval_key"].isin(
                non_purple_intervals
            )
        )
    ].copy()

    # Light red can be drawn over a dark-red base.
    # Keep the visible light-red unconfirmed stage.
    light_red_intervals = set(
        data.loc[
            data["fill_color_hex"] == "#F3AEA3",
            "interval_key",
        ]
    )

    data = data[
        ~(
            (data["fill_color_hex"] == "#DD0030")
            & data["interval_key"].isin(
                light_red_intervals
            )
        )
    ].copy()

    data = data.drop(
        columns=["interval_key"]
    )

    data["tfnsw_project_id"] = (
        data["project_row_id"]
        .astype(int)
        .map(
            lambda value: (
                f"TFNSW-{value:04d}"
            )
        )
    )

    data = data.sort_values(
        by=[
            "project_row_id",
            "start_quarter_index",
            "end_quarter_index",
        ]
    ).reset_index(drop=True)

    data["timeline_id"] = [
        f"TLS-{number:04d}"
        for number in range(
            1,
            len(data) + 1,
        )
    ]

    data = data.rename(
        columns={
            "x0": "source_x0",
            "x1": "source_x1",
            "shape_type": "source_shape_type",
        }
    )

    output_columns = [
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
    ]

    return data[output_columns]


def validate_output(
    project_rows,
    project_timeline,
):
    """Check the final timeline before saving it."""

    if len(project_rows) != 123:
        raise ValueError(
            "Expected 123 project rows, "
            f"but found {len(project_rows)}."
        )

    if (
        project_rows["project_name"]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicated project names were found."
        )

    represented_projects = (
        project_timeline[
            "tfnsw_project_id"
        ].nunique()
    )

    if represented_projects != 123:
        raise ValueError(
            "Expected timeline records for 123 projects, "
            f"but found {represented_projects}."
        )

    if len(project_timeline) != 225:
        raise ValueError(
            "Expected 225 timeline segments, "
            f"but found {len(project_timeline)}."
        )

    invalid_periods = project_timeline[
        project_timeline["end_quarter_index"]
        < project_timeline["start_quarter_index"]
    ]

    if not invalid_periods.empty:
        raise ValueError(
            "Timeline records with invalid periods "
            "were found."
        )

    duplicate_segments = (
        project_timeline.duplicated(
            subset=[
                "tfnsw_project_id",
                "stage_name",
                "timing_status",
                "start_quarter",
                "end_quarter",
            ]
        )
    )

    if duplicate_segments.any():
        raise ValueError(
            "Duplicated timeline segments were found."
        )


def main():
    """Build the TfNSW project timeline dataset."""

    words = pd.read_csv(
        WORDS_INPUT_FILE
    )

    shapes = pd.read_csv(
        SHAPES_INPUT_FILE
    )

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

    words["vertical_center"] = (
        words["top"] + words["bottom"]
    ) / 2

    project_groups = extract_project_groups(
        words
    )

    project_rows = reconstruct_project_rows(
        words,
        project_groups,
    )

    cleaned_shapes = clean_timeline_shapes(
        shapes
    )

    matched_shapes = match_shapes_to_projects(
        cleaned_shapes,
        project_rows,
    )

    project_timeline = (
        convert_shapes_to_timeline(
            matched_shapes
        )
    )

    validate_output(
        project_rows,
        project_timeline,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    project_timeline.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("Project groups:", len(project_groups))
    print("Project rows:", len(project_rows))
    print("Cleaned shapes:", len(cleaned_shapes))
    print("Matched shapes:", len(matched_shapes))
    print(
        "Final timeline segments:",
        len(project_timeline),
    )
    print(
        "Projects represented:",
        project_timeline[
            "tfnsw_project_id"
        ].nunique(),
    )

    print("\nValidation passed.")

    print("\nFile created:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()