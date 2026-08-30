"""Build visual table lines from positioned PDF words."""

import pandas as pd

from .config import (
    BODY_BOTTOM,
    BODY_TOP,
    COLUMN_BOUNDARIES,
    LINE_Y_TOLERANCE,
)


def _cluster_page_words(page_words: pd.DataFrame) -> list[list[dict]]:
    """Cluster words that share approximately the same vertical position."""

    ordered_words = page_words.sort_values(
        by=["top", "x0", "word_order"]
    ).to_dict("records")
    clusters: list[list[dict]] = []

    for word in ordered_words:
        if not clusters:
            clusters.append([word])
            continue

        current_top = sum(
            item["top"] for item in clusters[-1]
        ) / len(clusters[-1])

        if abs(word["top"] - current_top) <= LINE_Y_TOLERANCE:
            clusters[-1].append(word)
        else:
            clusters.append([word])

    return clusters


def _join_words(words: list[dict]) -> str:
    """Join words from left to right without changing their text."""

    return " ".join(
        str(word["text"])
        for word in sorted(words, key=lambda item: item["x0"])
    ).strip()


def _build_line(cluster: list[dict]) -> dict:
    """Turn one word cluster into a column-aligned visual line."""

    first_word = cluster[0]
    line = {
        "budget_year": first_word["budget_year"],
        "government_sector": first_word["government_sector"],
        "source_file": first_word["source_file"],
        "page_number": int(first_word["page_number"]),
        "line_top": min(word["top"] for word in cluster),
        "full_text": _join_words(cluster),
    }

    for column_name, (minimum_x, maximum_x) in (
        COLUMN_BOUNDARIES.items()
    ):
        column_words = [
            word
            for word in cluster
            if minimum_x <= word["x0"] < maximum_x
        ]
        line[column_name] = _join_words(column_words)

    return line


def build_visual_lines(words: pd.DataFrame) -> pd.DataFrame:
    """Reconstruct visual lines for every configured source page."""

    body_words = words.loc[
        (words["top"] >= BODY_TOP)
        & (words["bottom"] <= BODY_BOTTOM)
    ].copy()
    lines = []

    group_columns = [
        "budget_year",
        "government_sector",
        "source_file",
        "page_number",
    ]

    for _, page_words in body_words.groupby(
        group_columns,
        sort=False,
    ):
        for cluster in _cluster_page_words(page_words):
            lines.append(_build_line(cluster))

    return pd.DataFrame(lines).sort_values(
        by=[
            "budget_year",
            "government_sector",
            "page_number",
            "line_top",
        ]
    ).reset_index(drop=True)
