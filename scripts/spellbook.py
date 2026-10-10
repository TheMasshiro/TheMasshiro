#!/usr/bin/env python3
"""Draw the Spell Book: the real stack, annotated.

Contents follow the resume. An earlier version of this card was written from
guesswork and listed PostgreSQL, which has never been used here.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

W, H = 1000, 680
OUT = Path("profile/spellbook.svg")

# Headings are pinned to shared baselines so the two columns read as one spread.
LEFT = [
    (152, "OFFENSIVE MAGIC · SYSTEMS", [
        ("Rust", "a ward that refuses to let you be careless"),
        ("C", "the oldest spell here, still the sharpest"),
        ("C++", "the same spell, grown strange with age"),
        ("Assembly", "learned once, out of stubbornness"),
    ]),
    (374, "MEMORY VAULTS · DATABASES", [
        ("MongoDB", "a vault with no shelves, which is the point"),
        ("MySQL", "a vault that remembers enough"),
    ]),
]
RIGHT = [
    (152, "EVERYDAY SPELLS · WEB &amp; SCRIPTING", [
        ("TypeScript", "a plain spell, kept tidy"),
        ("JavaScript", "known by everyone, agreed on by no one"),
        ("Python", "for errands"),
    ]),
    (374, "SUMMONING CIRCLES · FRAMEWORKS", [
        ("React", "a familiar, summoned to redraw the window"),
        ("Tauri", "the same familiar, in a far smaller body"),
        ("Node.js", "errands, run on the other side of the wall"),
        ("Express", "a door, and someone to answer it"),
    ]),
]

PACK = ("Linux · Git · Docker · CI/CD · "
        "Neovim and VS Code, which do not speak to each other")


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
<line x1="70" y1="590" x2="930" y2="590" stroke="{f.RULE}" stroke-width="1"/>
<text x="500" y="620" text-anchor="middle" font-family="{f.SERIF}" font-size="13" font-style="italic" fill="{f.MUTED}"><tspan font-size="10" font-style="normal" letter-spacing="3" fill="{f.GOLD}" opacity="0.85">CARRIED IN THE PACK</tspan><tspan dx="14">{PACK}</tspan></text>
<text x="500" y="650" text-anchor="middle" font-family="{f.SERIF}" font-size="13" font-style="italic" fill="{f.MUTED}">Some are powerful. Some are not. Each one was worth learning.</text>
</g>'''
    OUT.write_text(f.card(W, H, body, mote_count=12, rng=random.Random(31)))
    print(f"{OUT}: {sum(len(s) for _, _, s in LEFT + RIGHT)} spells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
