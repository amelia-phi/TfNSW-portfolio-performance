from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "infrastructure_pipeline"
    / "Pipeline-28-08-2026.xlsx"
)

def load_transport_sheet(sheet_name, lifecycle):
    data = pd.read_excel(
        INPUT_FILE,
        sheet_name=sheet_name,
        header=1,
    )
    
    # Remove spaces from column names
    data.columns = data.columns.str.strip()

    # Remove columns containing no data
    data = data.dropna(axis=1, how="all")

    # Clean text columns
    text_columns = data.select_dtypes(include=["object"]).columns
    for column in text_columns:
        data[column] = data[column].str.strip()

    # Convert empty text to missing values
    data = data.replace("", pd.NA)

    # Remove completely empty rows
    data = data.dropna(axis=0, how="all")

    # Keep only Transport records
    data = data[data["Sector"] == "Transport"].copy()

    # Record the source lifecycle
    data["Source Lifecycle"] = lifecycle

    return data

def main():
    pipeline = load_transport_sheet(
        sheet_name="Pipeline",
        lifecycle="Pipeline",
    )

    in_planning = load_transport_sheet(
        sheet_name="In Planning",
        lifecycle="In Planning",
    )

    print("Pipeline Transport records:", len(pipeline))
    print("In Planning Transport records:", len(in_planning))

    combined = pd.concat(
        [pipeline, in_planning],
        ignore_index=True,
        sort=False,
    )

    print("Combined Transport records:", len(combined))
    print("\nColumns:")
    
    for column in combined.columns:
        print("-", column)

if __name__ == "__main__":
    main()
