"""Read and clean Infrastructure NSW workbook sheets."""

from pathlib import Path

import pandas as pd

from .config import HEADER_ROW, TARGET_SECTOR


def clean_transport_records(
    data: pd.DataFrame,
    lifecycle: str,
) -> pd.DataFrame:
    """Clean one source sheet and retain only Transport records."""

    cleaned = data.copy()
    cleaned.columns = cleaned.columns.str.strip()
    cleaned = cleaned.dropna(axis=1, how="all")

    text_columns = cleaned.select_dtypes(include=["str"]).columns
    for column in text_columns:
        cleaned[column] = cleaned[column].str.strip()

    cleaned = cleaned.replace("", pd.NA)
    cleaned = cleaned.dropna(axis=0, how="all")
    cleaned = cleaned[cleaned["Sector"] == TARGET_SECTOR].copy()
    cleaned = cleaned.dropna(axis=1, how="all")
    cleaned["Source Lifecycle"] = lifecycle
    return cleaned


def load_transport_sheet(
    input_file: Path,
    sheet_name: str,
    lifecycle: str,
) -> pd.DataFrame:
    """Read and clean one configured workbook sheet."""

    source_data = pd.read_excel(
        input_file,
        sheet_name=sheet_name,
        header=HEADER_ROW,
    )
    return clean_transport_records(source_data, lifecycle)
