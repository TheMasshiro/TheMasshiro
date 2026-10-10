#!/usr/bin/env python3
"""Draw Great Works: the things actually built, in the page's voice."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

W, H = 1000, 506
OUT = Path("profile/works.svg")

WORKS = [
    ("Legal counsel that never phones home", "SALENGA LAW FIRM", [
        "Gemma 4 E2B running fully offline on Android, iPhone and desktop, so",
        "client data never leaves the handset. Keyword search narrows 800 files",
        "to the four that matter. Tagalog, Jejemon and Taglish in, drafts out.",
    ]),
    ("BSFly IoT Platform", "LEAD DEVELOPER", [
        "Sensors, devices and alerts in real time across web and mobile, MQTT",
        "carrying telemetry from ESP32 to backend, buffered on the device so a",
        "dropped connection costs nothing.",
    ]),
    ("Fly Density Monitoring System", "DEVELOPER", [
        "Counting flies from a live camera at 83.34% mean accuracy, and 100%",
        "when the air is clear, with a multi-threaded capture pipeline that",
        "holds 86.67% against things that are not flies.",
    ]),
]


def work(y, title, role, lines):
    out = [
        f'<path d="M 74 {y-5} L 78 {y-1} L 74 {y+3} L 70 {y-1} Z" fill="{f.MINT}" opacity="0.7"/>',
        f'<text x="90" y="{y}" font-family="{f.SERIF}" font-size="18" fill="{f.LAV}">{title}</text>',
        f'<text x="930" y="{y}" text-anchor="end" font-family="{f.SERIF}" font-size="10" '
        f'letter-spacing="3" fill="{f.GOLD}" opacity="0.8">{role}</text>',
    ]
    for i, text in enumerate(lines):
        out.append(
            f'<text x="90" y="{y + 24 + i * 19}" font-family="{f.SERIF}" font-size="13" '
            f'font-style="italic" fill="{f.MUTED}">{text}</text>'
        )
    return "\n".join(out)


def main() -> int:
    blocks = "\n".join(
        work(150 + i * 108, title, role, lines)
        for i, (title, role, lines) in enumerate(WORKS)
    )
    body = f'''<g class="fade">
{f.heading(W, "Great Works", "DEEDS WORTH REMEMBERING", rule_y=106)}
{blocks}
<line x1="70" y1="452" x2="930" y2="452" stroke="{f.RULE}" stroke-width="1"/>
<text x="500" y="480" text-anchor="middle" font-family="{f.SERIF}" font-size="13" font-style="italic" fill="{f.MUTED}">The useful spells and the strange ones came from the same book.</text>
</g>'''
    OUT.write_text(f.card(W, H, body, mote_count=7, rng=random.Random(11)))
    print(f"{OUT}: {len(WORKS)} works")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
