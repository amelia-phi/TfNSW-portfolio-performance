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


def main():
    workbook = pd.ExcelFile(INPUT_FILE)

    print("Workbook:", INPUT_FILE.name)
    print("Sheets:", workbook.sheet_names)

    for sheet_name in workbook.sheet_names:
        data = pd.read_excel(
            INPUT_FILE,
            sheet_name=sheet_name,
            header=None,
        )

        print(
            f"{sheet_name}: "
            f"{data.shape[0]} rows × {data.shape[1]} columns"
        )


if __name__ == "__main__":
    main()
