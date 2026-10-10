#!/usr/bin/env python3
"""Draw The Calling: the specialization, the current post, the degree.

The page spent a long time describing how someone writes code without once
saying what they actually do. This is that, stated plainly.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

W, H = 1000, 262
OUT = Path("profile/calling.svg")

SPECIALIZATION = "Embedded Systems &amp; Firmware Engineering"
POST = ("Full-stack Developer", "Salenga Law Firm", "since August 2026")
DEGREE = ("BS Computer Engineering", "President Ramon Magsaysay State University")


def line(y, pieces, size, gap=14):
    """One centred row of alternating bright and muted pieces."""
    spans = "".join(
        f'<tspan fill="{f.LAV if bright else f.MUTED}">{text}</tspan>'
        + (f'<tspan fill="{f.RULE}" dx="{gap}" dy="0">·</tspan><tspan dx="{gap}"> </tspan>'
           if i < len(pieces) - 1 else "")
        for i, (text, bright) in enumerate(pieces)
    )
    return (f'<text x="{W//2}" y="{y}" text-anchor="middle" font-family="{f.SERIF}" '
            f'font-size="{size}">{spans}</text>')


def main() -> int:
    body = f'''<g class="fade">
{f.heading(W, "The Calling", "WHAT THE MAGE ACTUALLY DOES", rule_y=106)}
<text x="{W//2}" y="156" text-anchor="middle" font-family="{f.SERIF}" font-size="31" font-style="italic" fill="{f.MINT}" filter="url(#glow)">{SPECIALIZATION}</text>
{line(196, [(POST[0], True), (POST[1], True), (POST[2], False)], 14)}
{line(226, [(DEGREE[0], False), (DEGREE[1], False)], 13)}
</g>'''
    OUT.write_text(f.card(W, H, body, mote_count=6, rng=random.Random(7)))
    print(f"{OUT}: {SPECIALIZATION.replace('&amp;', '&')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
