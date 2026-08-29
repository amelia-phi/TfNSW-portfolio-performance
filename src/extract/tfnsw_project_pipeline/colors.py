"""Reusable PDF colour conversion helpers."""


def format_color(color) -> str | None:
    """Convert a PDF colour value into stable readable text."""

    if color is None:
        return None
    if isinstance(color, (tuple, list)):
        return ", ".join(f"{float(component):.4f}" for component in color)
    return str(color)


def rgb_to_hex(color) -> str | None:
    """Convert a three-component PDF RGB colour into hexadecimal."""

    if not isinstance(color, (tuple, list)) or len(color) != 3:
        return None

    rgb_values = []
    for component in color:
        bounded_component = max(0, min(1, float(component)))
        rgb_values.append(round(bounded_component * 255))

    red, green, blue = rgb_values
    return f"#{red:02X}{green:02X}{blue:02X}"
