#!/usr/bin/env python3
"""Draw the Spell Book: what got collected along the way, and what it cost."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

W, H = 1000, 600
OUT = Path("profile/spellbook.svg")

# Both columns pin their second heading to the same baseline so the page reads
# as one spread rather than two lists that happen to sit side by side.
LEFT = [
    (152, "OFFENSIVE MAGIC · SYSTEMS", [
        ("Rust", "a ward that refuses to let you be careless"),
        ("C", "the oldest spell here, still the sharpest"),
        ("C++", "the same spell, grown strange with age"),
        ("Assembly", "learned once, out of stubbornness"),
    ]),
    (372, "MEMORY VAULTS · DATABASES", [
        ("PostgreSQL", "a vault that remembers everything, exactly"),
        ("MySQL", "a vault that remembers enough"),
        ("MongoDB", "a vault with no shelves, which is the point"),
    ]),
]
RIGHT = [
    (152, "EVERYDAY SPELLS · WEB &amp; SCRIPTING", [
        ("TypeScript", "a plain spell, kept tidy"),
        ("JavaScript", "known by everyone, agreed on by no one"),
        ("Python", "for errands"),
    ]),
    (372, "SPELLS OF NO PARTICULAR USE", [
        ("Vim", "a spell for leaving, eventually"),
        ("VSCode", "the one that actually closes"),
        ("Shell", "written at midnight, never read again"),
    ]),
]


def column(x, groups):
    out = []
    for head_y, head, spells in groups:
        out.append(
            f'<text x="{x}" y="{head_y}" font-family="{f.SERIF}" font-size="11" '
            f'letter-spacing="3" fill="{f.GOLD}" opacity="0.85">{head}</text>'
        )
        y = head_y + 30
        for name, note in spells:
            cy = y - 5
            out.append(
                f'<path d="M {x+4} {cy-4} L {x+8} {cy} L {x+4} {cy+4} L {x} {cy} Z" '
                f'fill="{f.MINT}" opacity="0.7"/>'
                f'<text x="{x+20}" y="{y}" font-family="{f.SERIF}" font-size="17" '
                f'fill="{f.LAV}">{name}</text>'
                f'<text x="{x+20}" y="{y+19}" font-family="{f.SERIF}" font-size="13" '
                f'font-style="italic" fill="{f.MUTED}">{note}</text>'
            )
            y += 43
    return "\n".join(out)


def main() -> int:
    body = f'''<g class="fade">
{f.heading(W, "The Spell Book", "COLLECTED ALONG THE WAY", size=34, rule_y=114)}
{column(70, LEFT)}
{column(530, RIGHT)}
<line x1="70" y1="542" x2="930" y2="542" stroke="{f.RULE}" stroke-width="1"/>
<text x="500" y="572" text-anchor="middle" font-family="{f.SERIF}" font-size="13" font-style="italic" fill="{f.MUTED}">Some are powerful. Some are not. Each one was worth learning.</text>
</g>'''
    OUT.write_text(f.card(W, H, body, mote_count=10, rng=random.Random(31)))
    print(f"{OUT}: {sum(len(s) for _, _, s in LEFT + RIGHT)} spells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
