"""Read words and drawing objects from the TfNSW projects PDF."""

from pathlib import Path

import pandas as pd
import pdfplumber

from .colors import format_color, rgb_to_hex
from .config import (
    MAX_TIMELINE_HEIGHT,
    MIN_TIMELINE_HEIGHT,
    MIN_TIMELINE_WIDTH,
    SHAPE_COLUMNS,
    WORD_COLUMNS,
)


def _word_record(word: dict, page_number: int, page) -> dict:
    """Create one normalised word-coordinate record."""

    return {
        "page_number": page_number,
        "page_width": page.width,
        "page_height": page.height,
        "text": word["text"],
        "x0": word["x0"],
        "x1": word["x1"],
        "top": word["top"],
        "bottom": word["bottom"],
    }


def _shape_record(shape: dict, page_number: int, page) -> dict:
    """Create one normalised shape, coordinate, and colour record."""

    width = shape.get("width", 0)
    height = shape.get("height", 0)
    fill_color = shape.get("non_stroking_color")
    stroke_color = shape.get("stroking_color")
    is_timeline_candidate = (
        shape.get("fill") is True
        and fill_color is not None
        and width >= MIN_TIMELINE_WIDTH
        and MIN_TIMELINE_HEIGHT <= height <= MAX_TIMELINE_HEIGHT
    )

    return {
        "page_number": page_number,
        "page_width": page.width,
        "page_height": page.height,
        "shape_type": shape.get("object_type"),
        "x0": shape.get("x0"),
        "x1": shape.get("x1"),
        "top": shape.get("top"),
        "bottom": shape.get("bottom"),
        "width": width,
        "height": height,
        "is_filled": shape.get("fill"),
        "is_stroked": shape.get("stroke"),
        "fill_color_rgb": format_color(fill_color),
        "fill_color_hex": rgb_to_hex(fill_color),
        "stroke_color_rgb": format_color(stroke_color),
        "is_timeline_candidate": is_timeline_candidate,
    }


def extract_pdf_content(input_file: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extract positioned words and coloured shapes from every PDF page."""

    word_records = []
    shape_records = []

    with pdfplumber.open(input_file) as pdf:
        print("Input file:", input_file.name)
        print("Pages:", len(pdf.pages))

        for page_number, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()
            rectangles = list(page.rects)
            curves = list(page.curves)

            print(
                f"Page {page_number}: "
                f"{len(words)} words, "
                f"{len(rectangles)} rectangles, "
                f"{len(curves)} curves"
            )

            word_records.extend(
                _word_record(word, page_number, page) for word in words
            )
            shape_records.extend(
                _shape_record(shape, page_number, page)
                for shape in rectangles + curves
            )

    words_data = pd.DataFrame(word_records, columns=list(WORD_COLUMNS))
    shapes_data = pd.DataFrame(shape_records, columns=list(SHAPE_COLUMNS))
    return words_data, shapes_data
