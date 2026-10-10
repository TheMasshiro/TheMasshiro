#!/usr/bin/env python3
"""Draw the contribution year as a meadow.

Replaces the snake, which was a borrowed widget in GitHub's own green and the
last thing on the page drawn in someone else's hand. The caption had been
promising flowers for a while, so the squares became blooms: quiet days stay
low and green, the best days open in her lavender.
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f
import github

W, H = 1000, 350
OUT = Path("profile/meadow.svg")
LOGIN_DEFAULT = "TheMasshiro"

X0, Y0, COLUMNS, STEP = 70, 146, 53, 16.2
ROW = 16

# Nothing, then deepening green, then her colour for the days that went well.
BLOOM = [("#141c30", 2.0), (f.STEM, 3.0), ("#5fa98c", 3.6), (f.MINT, 4.2), (f.LAV, 4.8)]


def grid(days):
    first = date.fromisoformat(days[0][0])
    # GitHub's columns start on Sunday; weekday() calls Monday zero.
    start = first - timedelta(days=(first.weekday() + 1) % 7)

    cells, labels, seen = [], [], set()
    for iso, level in days:
        day = date.fromisoformat(iso)
        column = (day - start).days // 7
        if column >= COLUMNS:
            continue
        row = (day.weekday() + 1) % 7
        cx = X0 + column * STEP
        cy = Y0 + row * ROW
        fill, radius = BLOOM[level]
        opacity = 0.5 if level == 0 else 0.92
        cells.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="{radius}" fill="{fill}" '
                     f'opacity="{opacity}"><title>{iso}</title></circle>')

        if day.month not in seen and day.day <= 7:
            seen.add(day.month)
            labels.append(
                f'<text x="{cx:.1f}" y="132" font-family="{f.SERIF}" font-size="9" '
                f'letter-spacing="1" fill="{f.MUTED}" opacity="0.8">'
                f'{day.strftime("%b").upper()}</text>'
            )
    return "\n".join(labels + cells)


def tile(cx, value, label):
    return (
        f'<text x="{cx}" y="302" text-anchor="middle" font-family="{f.SERIF}" '
        f'font-size="30" font-style="italic" fill="{f.CREAM}" filter="url(#glow)">{value}</text>'
        f'<text x="{cx}" y="324" text-anchor="middle" font-family="{f.SERIF}" '
        f'font-size="10" letter-spacing="3" fill="{f.LAV}" opacity="0.9">{label}</text>'
    )


def main() -> int:
    login = sys.argv[1] if len(sys.argv) > 1 else LOGIN_DEFAULT
    days, total = github.contributions(login)
    current, longest = github.streaks(days)

    body = f'''<g class="fade">
{f.heading(W, "Flowers Left Behind", "ONE BLOOM FOR EVERY DAY ON THE ROAD", rule_y=106)}
{grid(days)}
<line x1="70" y1="266" x2="930" y2="266" stroke="{f.RULE}" stroke-width="1"/>
{tile(250, f"{total:,}", "BLOOMS, LAST 12 MONTHS")}
{tile(500, f"{current:,}", "CURRENT STREAK")}
{tile(750, f"{longest:,}", "LONGEST STREAK")}
</g>'''

    OUT.write_text(f.card(W, H, body, mote_count=6, rng=random.Random(total)))
    print(f"{OUT}: {total:,} contributions, streak {current}, longest {longest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
