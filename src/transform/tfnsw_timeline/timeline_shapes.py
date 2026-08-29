"""Clean, match, and transform TfNSW timeline shapes."""

import pandas as pd

from .config import (
    OUTPUT_COLUMNS,
    QUARTERS,
    QUARTER_WIDTH,
    ROW_MATCH_TOLERANCE,
    STAGE_COLOR_MAP,
    TIMELINE_START_X,
)


def clean_timeline_shapes(shapes: pd.DataFrame) -> pd.DataFrame:
    """Keep valid timeline shapes and remove exact drawing duplicates."""

    candidate_mask = (
        shapes["is_timeline_candidate"].astype(str).str.lower().eq("true")
    )
    data = shapes[
        candidate_mask & shapes["fill_color_hex"].isin(STAGE_COLOR_MAP)
    ].copy()

    data = data.drop_duplicates(
        subset=[
            "page_number",
            "shape_type",
            "x0",
            "x1",
            "top",
            "bottom",
            "fill_color_hex",
        ]
    )
    data = data[
        (data["x0"] >= 160)
        & (data["x1"] <= data["page_width"] + 0.01)
        & (data["top"] >= 0)
        & (data["bottom"] <= data["page_height"])
    ].copy()
    data["shape_center"] = (data["top"] + data["bottom"]) / 2
    return data


def match_shapes_to_projects(
    shapes: pd.DataFrame,
    project_rows: pd.DataFrame,
) -> pd.DataFrame:
    """Match each timeline shape to the nearest project row on its page."""

    matched_records = []

    for _, shape in shapes.iterrows():
        page_projects = project_rows[
            project_rows["source_page"] == shape["page_number"]
        ].copy()
        if page_projects.empty:
            continue

        page_projects["match_distance"] = (
            page_projects["row_center"] - shape["shape_center"]
        ).abs()
        nearest_project = page_projects.loc[
            page_projects["match_distance"].idxmin()
        ]
        if nearest_project["match_distance"] > ROW_MATCH_TOLERANCE:
            continue

        record = shape.to_dict()
        record.update(
            {
                "project_row_id": nearest_project["project_row_id"],
                "project_name": nearest_project["project_name"],
                "project_group": nearest_project["project_group"],
                "estimated_value_code": nearest_project["estimated_value_code"],
                "delivery_type": nearest_project["delivery_type"],
                "source_page": nearest_project["source_page"],
                "match_distance": nearest_project["match_distance"],
            }
        )
        matched_records.append(record)

    return pd.DataFrame(matched_records)


def _add_quarter_fields(data: pd.DataFrame) -> pd.DataFrame:
    """Translate horizontal PDF coordinates into quarter labels."""

    transformed = data.copy()
    transformed["start_quarter_index"] = (
        ((transformed["x0"] - TIMELINE_START_X) / QUARTER_WIDTH)
        .round()
        .clip(lower=0, upper=len(QUARTERS) - 1)
        .astype(int)
    )
    end_boundary_index = (
        ((transformed["x1"] - TIMELINE_START_X) / QUARTER_WIDTH)
        .round()
        .clip(lower=1, upper=len(QUARTERS))
        .astype(int)
    )
    transformed["end_quarter_index"] = end_boundary_index - 1
    transformed = transformed[
        transformed["end_quarter_index"]
        >= transformed["start_quarter_index"]
    ].copy()

    quarter_lookup = dict(enumerate(QUARTERS))
    transformed["start_quarter"] = transformed["start_quarter_index"].map(
        quarter_lookup
    )
    transformed["end_quarter"] = transformed["end_quarter_index"].map(
        quarter_lookup
    )
    return transformed


def _add_stage_fields(data: pd.DataFrame) -> pd.DataFrame:
    """Translate PDF colours into stage and timing definitions."""

    transformed = data.copy()
    transformed["stage_name"] = transformed["fill_color_hex"].map(
        lambda color: STAGE_COLOR_MAP[color]["stage_name"]
    )
    transformed["timing_status"] = transformed["fill_color_hex"].map(
        lambda color: STAGE_COLOR_MAP[color]["timing_status"]
    )
    return transformed


def _remove_drawing_overlays(data: pd.DataFrame) -> pd.DataFrame:
    """Remove base shapes that sit underneath the visible timeline colour."""

    transformed = data.drop_duplicates(
        subset=[
            "project_row_id",
            "fill_color_hex",
            "start_quarter_index",
            "end_quarter_index",
        ]
    ).copy()
    interval_columns = [
        "project_row_id",
        "start_quarter_index",
        "end_quarter_index",
    ]
    transformed["interval_key"] = list(
        transformed[interval_columns].itertuples(index=False, name=None)
    )

    non_purple_intervals = set(
        transformed.loc[
            transformed["fill_color_hex"] != "#C3AAD2", "interval_key"
        ]
    )
    transformed = transformed[
        ~(
            (transformed["fill_color_hex"] == "#C3AAD2")
            & transformed["interval_key"].isin(non_purple_intervals)
        )
    ].copy()

    light_red_intervals = set(
        transformed.loc[
            transformed["fill_color_hex"] == "#F3AEA3", "interval_key"
        ]
    )
    transformed = transformed[
        ~(
            (transformed["fill_color_hex"] == "#DD0030")
            & transformed["interval_key"].isin(light_red_intervals)
        )
    ].copy()
    return transformed.drop(columns=["interval_key"])


def convert_shapes_to_timeline(matched_shapes: pd.DataFrame) -> pd.DataFrame:
    """Convert matched PDF shapes into the processed timeline schema."""

    data = _add_quarter_fields(matched_shapes)
    data = _add_stage_fields(data)
    data = _remove_drawing_overlays(data)

    data["tfnsw_project_id"] = data["project_row_id"].astype(int).map(
        lambda value: f"TFNSW-{value:04d}"
    )
    data = data.sort_values(
        by=["project_row_id", "start_quarter_index", "end_quarter_index"]
    ).reset_index(drop=True)
    data["timeline_id"] = [
        f"TLS-{number:04d}" for number in range(1, len(data) + 1)
    ]
    data = data.rename(
        columns={
            "x0": "source_x0",
            "x1": "source_x1",
            "shape_type": "source_shape_type",
        }
    )
    return data[list(OUTPUT_COLUMNS)]
