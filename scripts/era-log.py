#!/usr/bin/env python3
"""Draw the Era Log card: how long the journey has run, and how little that is.

Frieren measures a decade the way everyone else measures an afternoon, so the
card states the elapsed time plainly and then undercuts it. Rendered here
rather than fetched from a widget because no widget speaks in this voice.
"""

import random
from datetime import date
from pathlib import Path

JOURNEY_START = date(2024, 1, 31)
OUT = Path("profile/era.svg")

W, H = 1000, 250
SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"
LAV, MINT, GOLD = "#c9b8e8", "#8fd3b6", "#f6d98a"
CREAM, MUTED, RULE = "#f1ecff", "#8a93a8", "#2b2c55"


def elapsed(start: date, today: date) -> tuple[int, int, int]:
    months = (today.year - start.year) * 12 + (today.month - start.month)
    if today.day < start.day:
        months -= 1
    return months // 12, months % 12, (today - start).days


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def undercut(years: int) -> str:
    if years < 1:
        return "To an elf, a morning."
    if years < 5:
        return "To an elf, an afternoon."
    if years < 20:
        return "To an elf, a single season."
    return "To an elf, a short while."


def main() -> int:
    today = date.today()
    years, months, days = elapsed(JOURNEY_START, today)

    parts = [plural(years, "year")] if years else []
    parts.append(plural(months, "month"))
    span = ", ".join(parts)

    started = JOURNEY_START.strftime("%d %B %Y").lstrip("0")
    footing = f"since {started} · {days:,} days on the road"

    random.seed(days)
    motes = "\n".join(
        f'<circle class="mote" cx="{random.choice([random.uniform(16, 56), random.uniform(944, 984)]):.1f}" '
        f'cy="{random.uniform(170, 250):.1f}" r="{random.uniform(1.2, 2.0):.1f}" fill="#d9f5e8" '
        f'style="animation-delay:-{random.uniform(0, 9):.2f}s" filter="url(#glow)"/>'
        for _ in range(6)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <linearGradient id="page" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a0f20"/>
    <stop offset="1" stop-color="#070b18"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<style>
  .mote {{ animation: rise 9s linear infinite; }}
  @keyframes rise {{ 0% {{ transform: translateY(0); opacity: 0 }} 15% {{ opacity: .8 }} 85% {{ opacity: .5 }} 100% {{ transform: translateY(-120px); opacity: 0 }} }}
  .fade {{ animation: fadein 2.5s ease-out both; }}
  @keyframes fadein {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#page)"/>
{motes}
<g class="fade">
<text x="500" y="58" text-anchor="middle" font-family="{SERIF}" font-size="30" font-style="italic" letter-spacing="2" fill="{CREAM}" filter="url(#glow)">The Era Log</text>
<text x="500" y="84" text-anchor="middle" font-family="{SERIF}" font-size="11" letter-spacing="5" fill="{LAV}">· HOW LONG THE JOURNEY HAS RUN ·</text>
<line x1="70" y1="106" x2="930" y2="106" stroke="{RULE}" stroke-width="1"/>
<text x="500" y="158" text-anchor="middle" font-family="{SERIF}" font-size="40" font-style="italic" fill="{MINT}" filter="url(#glow)">{span}</text>
<text x="500" y="186" text-anchor="middle" font-family="{SERIF}" font-size="12" letter-spacing="1" fill="{MUTED}">{footing}</text>
<text x="500" y="220" text-anchor="middle" font-family="{SERIF}" font-size="15" font-style="italic" fill="{GOLD}" opacity="0.9">{undercut(years)}</text>
</g>
</g></svg>
'''
    OUT.write_text(svg)
    print(f"{OUT}: {span} ({days:,} days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
