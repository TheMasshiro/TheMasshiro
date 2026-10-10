#!/usr/bin/env python3
"""Repaint the language colors in a top-langs card with the Frieren palette.

github-readme-stats paints each language with GitHub's canonical color, which
has no override option and drags a rainbow into an otherwise pastel README.
The card emits colors in language order, so we collect the ones that are not
part of the card chrome and remap them to the banner palette, biggest share
first. If the card ever stops looking like this, nothing is changed.
"""

import re
import sys
from pathlib import Path

# Soft lavender to pale mint, lifted from profile/banner.svg.
RAMP = ["#c9b8e8", "#8fd3b6", "#f6d98a", "#9ec5f0", "#f2b8d0", "#d9f5e8"]

# Colors the card draws for itself: background, title, label text, masks, and
# the border stroke, which is emitted with stroke-opacity 0 even when hidden.
CHROME = {
    "#0d1117", "#c9b8e8", "#c9d1d9", "#e4e2e2",
    "#ffffff", "#000000", "#fff", "#000",
}

HEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")


def repaint(svg: str) -> tuple[str, dict[str, str]]:
    seen = []
    for color in HEX.findall(svg):
        lowered = color.lower()
        if lowered not in CHROME and lowered not in seen:
            seen.append(lowered)

    mapping = {old: RAMP[i % len(RAMP)] for i, old in enumerate(seen)}
    for old, new in mapping.items():
        svg = re.sub(re.escape(old), new, svg, flags=re.IGNORECASE)
    return svg, mapping


def main() -> int:
    path = Path(sys.argv[1])
    svg = path.read_text()
    repainted, mapping = repaint(svg)

    if not mapping:
        print(f"{path}: no language colors found, leaving it alone")
        return 0

    path.write_text(repainted)
    for old, new in mapping.items():
        print(f"{path}: {old} -> {new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
