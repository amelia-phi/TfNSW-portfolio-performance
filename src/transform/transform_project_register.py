from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "infrastructure_pipeline_transport_raw.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "project_register.csv"
)


REQUIRED_COLUMNS = {
    "Sector",
    "Project name",
    "Estimated Value",
    "Project Link",
    "Source Lifecycle",
}


def validate_input(data):
    """Check that the interim extract is suitable for transformation."""

    missing_columns = REQUIRED_COLUMNS.difference(
        data.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if len(data) != 99:
        raise ValueError(
            "Expected 99 source records, "
            f"but found {len(data)}."
        )

    if data["Project name"].isna().any():
        raise ValueError(
            "One or more records have a missing project name."
        )

    invalid_sectors = data.loc[
        data["Sector"] != "Transport",
        "Sector",
    ].unique()

    if len(invalid_sectors) > 0:
        raise ValueError(
            "Non-Transport records found: "
            + ", ".join(invalid_sectors)
        )

    valid_lifecycles = {
        "Pipeline",
        "In Planning",
    }

    invalid_lifecycles = set(
        data["Source Lifecycle"].dropna().unique()
    ).difference(valid_lifecycles)

    if invalid_lifecycles:
        raise ValueError(
            "Unexpected source lifecycles: "
            + ", ".join(sorted(invalid_lifecycles))
        )


def main():
    """Build the processed project register."""

    data = pd.read_csv(INPUT_FILE)

    print("Input file:", INPUT_FILE.name)
    print("Input records:", len(data))
    print("Input columns:", len(data.columns))

    validate_input(data)

    print("Input validation passed.")


if __name__ == "__main__":
    main()