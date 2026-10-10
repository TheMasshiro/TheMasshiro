"""Shared drawing kit for the profile cards.

Every card is the same object: a rounded dark page, a serif title over a hair
rule, and motes drifting up the margins. Keeping that here means a card script
is only its own content, and the page cannot drift out of one hand.
"""

import random

SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"

LAV = "#c9b8e8"     # her hair
MINT = "#8fd3b6"    # her eyes
GOLD = "#f6d98a"    # the trim on the robe
PINK = "#f2b8d0"
SKY = "#9ec5f0"
CREAM = "#f1ecff"
PALE = "#d9f5e8"
MUTED = "#8a93a8"
RULE = "#2b2c55"
STEM = "#3f7a68"

RAMP = [LAV, MINT, GOLD, SKY, PINK, PALE]

CHROME = f"""<defs>
  <linearGradient id="page" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a0f20"/>
    <stop offset="1" stop-color="#070b18"/>
  </linearGradient>
  <linearGradient id="meadow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1d3b35"/>
    <stop offset="1" stop-color="#0c1a17"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{{w}}" height="{{h}}" rx="16"/></clipPath>
</defs>
<style>
  .mote {{{{ animation: rise 9s linear infinite; }}}}
  @keyframes rise {{{{ 0% {{{{ transform: translateY(0); opacity: 0 }}}} 15% {{{{ opacity: .8 }}}} 85% {{{{ opacity: .5 }}}} 100% {{{{ transform: translateY(-140px); opacity: 0 }}}} }}}}
  .sway {{{{ transform-box: fill-box; transform-origin: 50% 100%; animation: sway 4s ease-in-out infinite; }}}}
  @keyframes sway {{{{ 0%,100% {{{{ transform: rotate(-4deg) }}}} 50% {{{{ transform: rotate(4deg) }}}} }}}}
  .fade {{{{ animation: fadein 2.5s ease-out both; }}}}
  @keyframes fadein {{{{ from {{{{ opacity: 0 }}}} to {{{{ opacity: 1 }}}} }}}}
</style>"""


def motes(w, h, count=8, rng=None):
    """Drifting lights, kept to the outer margins so they never cross text."""
    rng = rng or random
    out = []
    for _ in range(count):
        x = rng.choice([rng.uniform(16, 56), rng.uniform(w - 56, w - 16)])
        out.append(
            f'<circle class="mote" cx="{x:.1f}" cy="{rng.uniform(h - 130, h):.1f}" '
            f'r="{rng.uniform(1.2, 2.1):.1f}" fill="{PALE}" '
            f'style="animation-delay:-{rng.uniform(0, 9):.2f}s" filter="url(#glow)"/>'
        )
    return "\n".join(out)


def heading(w, title, subtitle, size=30, rule_y=None):
    out = [
        f'<text x="{w//2}" y="58" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="{size}" font-style="italic" letter-spacing="2" fill="{CREAM}" '
        f'filter="url(#glow)">{title}</text>',
        f'<text x="{w//2}" y="84" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="11" letter-spacing="5" fill="{LAV}">· {subtitle} ·</text>',
    ]
    if rule_y:
        out.append(
            f'<line x1="70" y1="{rule_y}" x2="{w-70}" y2="{rule_y}" '
            f'stroke="{RULE}" stroke-width="1"/>'
        )
    return "\n".join(out)


def card(w, h, body, mote_count=8, rng=None):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{CHROME.format(w=w, h=h)}
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#page)"/>
{motes(w, h, mote_count, rng)}
{body}
</g></svg>
'''
