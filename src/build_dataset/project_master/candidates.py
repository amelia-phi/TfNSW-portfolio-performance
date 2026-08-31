"""Generate possible matches between project data sources."""

from difflib import SequenceMatcher
from itertools import combinations

import pandas as pd

from .config import MINIMUM_CANDIDATE_SCORE


def token_sort_text(value: str) -> str:
    """Sort words so that word order has less effect on matching."""

    return " ".join(sorted(value.split()))


def calculate_similarity(
    left_name: str,
    right_name: str,
) -> float:
    """Calculate similarity between two normalised names."""

    if not left_name or not right_name:
        return 0.0

    direct_score = SequenceMatcher(
        None,
        left_name,
        right_name,
    ).ratio()

    token_score = SequenceMatcher(
        None,
        token_sort_text(left_name),
        token_sort_text(right_name),
    ).ratio()

    return round(
        max(direct_score, token_score),
        4,
    )