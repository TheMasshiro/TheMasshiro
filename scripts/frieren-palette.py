#!/usr/bin/env python3
"""Repaint the language colors in a top-langs card with the Frieren palette.

github-readme-stats paints each language with GitHub's canonical color, which
has no override option and drags a rainbow into an otherwise pastel README.

Language colors are the only ones the card writes as fill="..." presentation
attributes on its marks. Its own chrome lives either in the <style> block or on
the frame rect, so both are lifted out before scanning rather than kept in a
blocklist of specific colors, which would quietly rot whenever upstream picks a
new default.
"""

import re
import sys
from pathlib import Path

# Soft lavender to pale mint, lifted from profile/banner.svg.
RAMP = ["#c9b8e8", "#8fd3b6", "#f6d98a", "#9ec5f0", "#f2b8d0", "#d9f5e8"]

# The unfilled part of the progress bar is hardcoded light grey in the card's
# stylesheet and ignores every theme option, so it is set directly.
TRACK_FROM, TRACK_TO = "#ddd", "#1b2233"

STYLE = re.compile(r"<style>.*?</style>", re.S)
FRAME = re.compile(r"<rect[^>]*stroke-opacity[^>]*/>", re.S)
FILL = re.compile(r'fill="(#(?:[0-9a-fA-F]{3}){1,2})"')


def language_colors(svg: str) -> list[str]:
    """Ordered, de-duplicated language colors, biggest share first."""
    marks = FRAME.sub("", STYLE.sub("", svg))
    seen = []
    for color in FILL.findall(marks):
        lowered = color.lower()
        if lowered not in seen:
            seen.append(lowered)
    return seen


def repaint(svg: str) -> tuple[str, dict[str, str]]:
    mapping = {old: RAMP[i % len(RAMP)] for i, old in enumerate(language_colors(svg))}
    for old, new in mapping.items():
        # The boundary keeps a short color such as #ddd from matching the first
        # half of a long one.
        svg = re.sub(re.escape(old) + r"\b", new, svg, flags=re.IGNORECASE)

    if TRACK_FROM in svg:
        svg = re.sub(re.escape(TRACK_FROM) + r"\b", TRACK_TO, svg)
        mapping[TRACK_FROM] = TRACK_TO
    return svg, mapping


def main() -> int:
    path = Path(sys.argv[1])
    repainted, mapping = repaint(path.read_text())

    if not mapping:
        print(f"{path}: nothing to repaint, leaving it alone")
        return 0

    path.write_text(repainted)
    for old, new in mapping.items():
        print(f"{path}: {old} -> {new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
