# standardise project names before matching
# while preserving important distinctions

"""Normalise project names for cross-source matching."""

import re
import unicodedata

import pandas as pd

def normalise_text(value: object) -> str:
    """Convert text into a consistent format for comparison."""

    if pd.isna(value):
        return ""

    text = str(value)

    # Standardise Unicode characters.
    text = unicodedata.normalize("NFKC", text)

    # Treat ampersands as the word "and".
    text = text.replace("&", " and ")

    # Treat different dash characters consistently.
    text = re.sub(r"[‐‑‒–—−-]", " ", text)

    # Make matching case-insensitive.
    text = text.casefold()

    # Remove punctuation but retain letters and numbers.
    text = re.sub(r"[^\w\s]", " ", text)

    # Replace repeated spaces with one space.
    text = re.sub(r"\s+", " ", text).strip()

    return text

def normalise_project_name(project_name: object) -> str:
    """Create a conservative normalised project name."""

    return normalise_text(project_name)

def normalise_source_projects(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Add a normalised name to every source project."""

    required_column = "source_project_name"

    if required_column not in data.columns:
        raise ValueError(
            f"Missing required column: {required_column}"
        )

    result = data.copy()

    result["normalised_project_name"] = (
        result["source_project_name"]
        .map(normalise_project_name)
    )

    blank_names = (
        result["normalised_project_name"]
        .eq("")
    )

    if blank_names.any():
        raise ValueError(
            "One or more project names became blank "
            "during normalisation."
        )

    return result