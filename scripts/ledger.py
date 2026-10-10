#!/usr/bin/env python3
"""Draw the Traveler's Ledger: the counts, and which spells get cast most.

Replaces two third-party cards with one. They were the last things on the page
carrying someone else's typeface and corner radius, and splitting the numbers
from the languages was never anything but an artifact of their being separate
widgets.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f
import github

W, H = 1000, 390
OUT = Path("profile/ledger.svg")
LOGIN_DEFAULT = "TheMasshiro"
TOP_LANGS = 6


def tile(cx, value, label):
    return (
        f'<text x="{cx}" y="168" text-anchor="middle" font-family="{f.SERIF}" '
        f'font-size="38" font-style="italic" fill="{f.CREAM}" filter="url(#glow)">{value}</text>'
        f'<text x="{cx}" y="194" text-anchor="middle" font-family="{f.SERIF}" '
        f'font-size="10" letter-spacing="3" fill="{f.LAV}" opacity="0.9">{label}</text>'
    )


def bar(langs, total, x0=70, y=272, width=860, height=10):
    """One rounded rail, divided by share. Short slices still get a sliver."""
    out = [f'<clipPath id="rail"><rect x="{x0}" y="{y}" width="{width}" '
           f'height="{height}" rx="{height/2}"/></clipPath>',
           f'<rect x="{x0}" y="{y}" width="{width}" height="{height}" '
           f'rx="{height/2}" fill="#1b2233"/>']
    cursor = x0
    for i, (_, size) in enumerate(langs):
        span = max(width * size / total, 3)
        out.append(f'<rect clip-path="url(#rail)" x="{cursor:.1f}" y="{y}" '
                   f'width="{span:.1f}" height="{height}" fill="{f.RAMP[i % len(f.RAMP)]}"/>')
        cursor += span
    return "\n".join(out)


def legend(langs, total, x0=70, y=318, step=28, columns=3, column_width=287):
    out = []
    for i, (name, size) in enumerate(langs):
        cx = x0 + (i % columns) * column_width
        cy = y + (i // columns) * step
        out.append(
            f'<circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{f.RAMP[i % len(f.RAMP)]}"/>'
            f'<text x="{cx+18}" y="{cy}" font-family="{f.SERIF}" font-size="13" '
            f'fill="{f.MUTED}">{name} <tspan fill="{f.LAV}">{size/total:.1%}</tspan></text>'
        )
    return "\n".join(out)


def main() -> int:
    login = sys.argv[1] if len(sys.argv) > 1 else LOGIN_DEFAULT

    owned = github.repos(login)
    _, contributed = github.contributions(login)
    prs = github.search_count(f"issues:author:{login}+type:pr")
    langs_all = github.language_bytes(login, owned)
    langs = list(langs_all.items())[:TOP_LANGS]
    total_bytes = sum(size for _, size in langs)

    body = f'''<g class="fade">
{f.heading(W, "The Traveler's Ledger", "WHAT THE ROAD HAS ADDED UP TO", rule_y=106)}
{tile(125, f"{contributed:,}", "CONTRIBUTIONS, LAST YEAR")}
{tile(375, f"{prs:,}", "PULL REQUESTS OPENED")}
{tile(625, f"{len(owned):,}", "REPOSITORIES KEPT")}
{tile(875, f"{len(langs_all):,}", "LANGUAGES WRITTEN")}
<line x1="70" y1="228" x2="930" y2="228" stroke="{f.RULE}" stroke-width="1"/>
<text x="70" y="256" font-family="{f.SERIF}" font-size="11" letter-spacing="3" fill="{f.GOLD}" opacity="0.85">SPELLS MOST CAST</text>
{bar(langs, total_bytes)}
{legend(langs, total_bytes)}
</g>'''

    OUT.write_text(f.card(W, H, body, mote_count=8, rng=random.Random(contributed)))
    print(f"{OUT}: {contributed:,} contributions, {prs} PRs, "
          f"{len(owned)} repos, {len(langs_all)} languages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
