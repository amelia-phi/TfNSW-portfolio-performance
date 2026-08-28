from pathlib import Path
import logging

import pandas as pd
import pdfplumber


# Hide harmless font warnings from the PDF parser
logging.getLogger("pdfminer").setLevel(logging.ERROR)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "tfnsw_pipeline"
    / "tfnsw-infrastructure-projects-pipeline-july-2026.pdf"
)

WORDS_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_words.csv"
)

SHAPES_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "tfnsw_project_pipeline_shapes.csv"
)


WORD_COLUMNS = [
    "page_number",
    "page_width",
    "page_height",
    "text",
    "x0",
    "x1",
    "top",
    "bottom",
]

SHAPE_COLUMNS = [
    "page_number",
    "page_width",
    "page_height",
    "shape_type",
    "x0",
    "x1",
    "top",
    "bottom",
    "width",
    "height",
    "is_filled",
    "is_stroked",
    "fill_color_rgb",
    "fill_color_hex",
    "stroke_color_rgb",
    "is_timeline_candidate",
]


def validate_input():
    """Confirm that the projects pipeline PDF exists."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Projects pipeline PDF not found: {INPUT_FILE}"
        )

    if INPUT_FILE.suffix.lower() != ".pdf":
        raise ValueError(
            "Projects pipeline source is not a PDF."
        )


def format_color(color):
    """Convert a PDF colour into readable text."""

    if color is None:
        return None

    if isinstance(color, (tuple, list)):
        return ", ".join(
            f"{float(component):.4f}"
            for component in color
        )

    return str(color)


def rgb_to_hex(color):
    """Convert a three-part PDF RGB colour to hexadecimal."""

    if not isinstance(color, (tuple, list)):
        return None

    if len(color) != 3:
        return None

    rgb_values = []

    for component in color:
        component = float(component)

        # Keep the value inside the valid PDF RGB range
        component = max(0, min(1, component))

        rgb_values.append(
            round(component * 255)
        )

    red, green, blue = rgb_values

    return f"#{red:02X}{green:02X}{blue:02X}"


def extract_pdf_content():
    """Extract words, shapes, positions and colours."""

    word_records = []
    shape_records = []

    with pdfplumber.open(INPUT_FILE) as pdf:
        print("Input file:", INPUT_FILE.name)
        print("Pages:", len(pdf.pages))

        for page_number, page in enumerate(
            pdf.pages,
            start=1,
        ):
            words = page.extract_words()

            rectangles = list(page.rects)
            curves = list(page.curves)

            print(
                f"Page {page_number}: "
                f"{len(words)} words, "
                f"{len(rectangles)} rectangles, "
                f"{len(curves)} curves"
            )

            for word in words:
                word_records.append(
                    {
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

            page_shapes = rectangles + curves

            for shape in page_shapes:
                width = shape.get("width", 0)
                height = shape.get("height", 0)

                fill_color = shape.get(
                    "non_stroking_color"
                )

                stroke_color = shape.get(
                    "stroking_color"
                )

                # Initial rule for identifying shapes that
                # resemble the coloured timeline bars
                is_timeline_candidate = (
                    shape.get("fill") is True
                    and fill_color is not None
                    and width >= 3
                    and 5 <= height <= 10
                )

                shape_records.append(
                    {
                        "page_number": page_number,
                        "page_width": page.width,
                        "page_height": page.height,
                        "shape_type": shape.get(
                            "object_type"
                        ),
                        "x0": shape.get("x0"),
                        "x1": shape.get("x1"),
                        "top": shape.get("top"),
                        "bottom": shape.get("bottom"),
                        "width": width,
                        "height": height,
                        "is_filled": shape.get("fill"),
                        "is_stroked": shape.get(
                            "stroke"
                        ),
                        "fill_color_rgb": format_color(
                            fill_color
                        ),
                        "fill_color_hex": rgb_to_hex(
                            fill_color
                        ),
                        "stroke_color_rgb": format_color(
                            stroke_color
                        ),
                        "is_timeline_candidate": (
                            is_timeline_candidate
                        ),
                    }
                )

    words_data = pd.DataFrame(
        word_records,
        columns=WORD_COLUMNS,
    )

    shapes_data = pd.DataFrame(
        shape_records,
        columns=SHAPE_COLUMNS,
    )

    return words_data, shapes_data


def save_output(data, output_file):
    """Save an extracted dataset as a CSV file."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        output_file,
        index=False,
    )


def main():
    """Extract the TfNSW projects pipeline PDF."""

    validate_input()

    words_data, shapes_data = extract_pdf_content()

    if words_data.empty:
        raise ValueError(
            "No words were extracted from the projects PDF."
        )

    if shapes_data.empty:
        raise ValueError(
            "No shapes were extracted from the projects PDF."
        )

    save_output(
        words_data,
        WORDS_OUTPUT_FILE,
    )

    save_output(
        shapes_data,
        SHAPES_OUTPUT_FILE,
    )

    timeline_candidate_count = (
        shapes_data["is_timeline_candidate"].sum()
    )

    print("\nExtraction complete")
    print("Total words:", len(words_data))
    print("Total shapes:", len(shapes_data))
    print(
        "Possible timeline shapes:",
        timeline_candidate_count,
    )

    print("\nFiles created:")
    print(WORDS_OUTPUT_FILE)
    print(SHAPES_OUTPUT_FILE)


if __name__ == "__main__":
    main()