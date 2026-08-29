"""Reconstruct project groups and project rows from positioned PDF words."""

import pandas as pd


def add_vertical_centers(words: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the word extract with a vertical centre coordinate."""

    prepared_words = words.copy()
    prepared_words["vertical_center"] = (
        prepared_words["top"] + prepared_words["bottom"]
    ) / 2
    return prepared_words


def extract_project_groups(words: pd.DataFrame) -> pd.DataFrame:
    """Extract headings such as Central Coast roads."""

    group_records = []
    data_set_labels = words[(words["text"] == "Set") & (words["x0"] > 500)]

    for _, label in data_set_labels.iterrows():
        page_number = label["page_number"]
        label_center = label["vertical_center"]

        group_words = words[
            (words["page_number"] == page_number)
            & (words["x0"] < 160)
            & ((words["vertical_center"] - label_center).abs() <= 12)
        ].sort_values(by=["top", "x0"])

        group_records.append(
            {
                "page_number": page_number,
                "group_center": label_center,
                "project_group": " ".join(group_words["text"].astype(str)),
            }
        )

    return (
        pd.DataFrame(group_records)
        .sort_values(by=["page_number", "group_center"])
        .reset_index(drop=True)
    )


def reconstruct_project_rows(
    words: pd.DataFrame,
    project_groups: pd.DataFrame,
) -> pd.DataFrame:
    """Rebuild project records using value codes as row anchors."""

    value_anchors = words[
        words["text"].astype(str).str.fullmatch(r"\${1,6}|TBA", na=False)
        & words["x0"].between(88, 120)
    ].sort_values(by=["page_number", "top"])

    project_records = []

    for _, anchor in value_anchors.iterrows():
        page_number = anchor["page_number"]
        row_center = anchor["vertical_center"]

        row_words = words[
            (words["page_number"] == page_number)
            & ((words["vertical_center"] - row_center).abs() <= 15.5)
        ]

        project_name = " ".join(
            row_words[row_words["x0"] < 92]
            .sort_values(by=["top", "x0"])["text"]
            .astype(str)
        )
        delivery_type = " ".join(
            row_words[(row_words["x0"] >= 120) & (row_words["x0"] < 161)]
            .sort_values(by=["top", "x0"])["text"]
            .astype(str)
        )

        if project_name == "Project" and delivery_type == "Delivery type":
            continue

        earlier_groups = project_groups[
            (project_groups["page_number"] < page_number)
            | (
                (project_groups["page_number"] == page_number)
                & (project_groups["group_center"] < row_center)
            )
        ]
        project_group = (
            pd.NA
            if earlier_groups.empty
            else earlier_groups.iloc[-1]["project_group"]
        )

        project_records.append(
            {
                "project_row_id": len(project_records) + 1,
                "project_name": project_name,
                "project_group": project_group,
                "estimated_value_code": anchor["text"],
                "delivery_type": delivery_type,
                "source_page": page_number,
                "row_center": row_center,
            }
        )

    return pd.DataFrame(project_records)
