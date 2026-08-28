from pathlib import Path
import logging

import pandas as pd
import pdfplumber


# Hide harmless PDF font warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILES = {
    "projects": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "tfnsw_pipeline"
        / "tfnsw-infrastructure-projects-pipeline-july-2026.pdf"
    ),
}

OUTPUT_FILES = {
    "projects": (
        PROJECT_ROOT
        / "data"
        / "interim"
        / "tfnsw_projects_words.csv"
    ),
}

WORD_COLUMNS = [
    "pipeline_type",
    "page_number",
    "page_width",
    "page_height",
    "text",
    "x0",
    "x1",
    "top",
    "bottom",
]


def validate_inputs():
    """Confirm that expected PDF files exist."""

    for pipeline_type, file_path in SOURCE_FILES.items():
        if not file_path.exists():
            raise FileNotFoundError(
                f"{pipeline_type.title()} PDF not found: "
                f"{file_path}"
            )

        if file_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"{pipeline_type.title()} source is not a PDF."
            )


def extract_words(pipeline_type, file_path):
    """Extract words and their positions from one PDF."""

    records = []

    with pdfplumber.open(file_path) as pdf:
        print("\nPipeline type:", pipeline_type)
        print("Input file:", file_path.name)
        print("Pages:", len(pdf.pages))

        for page_number, page in enumerate(
            pdf.pages,
            start=1,
        ):
            words = page.extract_words()

            print(
                f"Page {page_number}: "
                f"{len(words)} words"
            )

            for word in words:
                records.append(
                    {
                        "pipeline_type": pipeline_type,
                        "page_number": page_number,
                        "page_width": page.width,
                        "page_height": page.height,
                        "text": word["text"],
                        "x0": word["x0"],
                        "x1": word["x1"],
                        "top": word["top"],
                        "bottom": word["bottom"],
                    }
                )

    return pd.DataFrame(
        records,
        columns=WORD_COLUMNS,
    )


def main():
    """Extract positioned words from both TfNSW PDFs."""

    validate_inputs()

    for pipeline_type, input_file in SOURCE_FILES.items():
        extracted_words = extract_words(
            pipeline_type,
            input_file,
        )

        output_file = OUTPUT_FILES[pipeline_type]

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        extracted_words.to_csv(
            output_file,
            index=False,
        )

        print("Total extracted words:", len(extracted_words))
        print("File created:")
        print(output_file)


if __name__ == "__main__":
    main()