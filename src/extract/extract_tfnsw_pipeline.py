from pathlib import Path

import pdfplumber


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILES = {
    "projects": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "tfnsw_pipeline"
        / "tfnsw-infrastructure-projects-pipeline-july-2026.pdf"
    ),
    "maintenance": (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "tfnsw_pipeline"
        / "TfNSW-infrastructure-maintenance-pipeline-july-2026.pdf"
    ),
}


def validate_inputs():
    """Confirm that both expected PDF files exist."""

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


def main():
    """Inspect the TfNSW projects and maintenance PDFs."""

    validate_inputs()


if __name__ == "__main__":
    main()