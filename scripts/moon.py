#!/usr/bin/env python3
"""Put tonight's real moon over the meadow.

The banner was drawn with a fixed crescent. CI runs nightly, so the moon can
just be the one that is actually up. An elf who has watched the same moon for
a thousand years should at least be watching the right one.

Mean phase only, no perturbations, which lands within about half a day. That
is well inside the width of the line being drawn.
"""

import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

BANNER = Path("profile/banner.svg")
CX, CY, R = 860, 70, 30

# A known new moon, and the mean interval between them.
EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
SYNODIC = 29.530588853

NAMES = [
    (0.02, "New Moon"), (0.23, "Waxing Crescent"), (0.27, "First Quarter"),
    (0.48, "Waxing Gibbous"), (0.52, "Full Moon"), (0.73, "Waning Gibbous"),
    (0.77, "Last Quarter"), (0.98, "Waning Crescent"), (1.01, "New Moon"),
]


def phase_of(when: datetime) -> float:
    """Fraction through the cycle: 0 new, 0.25 first quarter, 0.5 full."""
    return ((when - EPOCH).total_seconds() / 86400.0 % SYNODIC) / SYNODIC


def name_of(phase: float) -> str:
    return next(name for edge, name in NAMES if phase < edge)


def lit_path(phase: float) -> str:
    """The lit crescent, as a limb arc closed by the terminator.

    The terminator is the ellipse whose width tracks cos of the phase angle:
    hugging the limb at new moon, flat at the quarters, and bulging across to
    the far limb at full. An rx of zero degrades to a straight line, which is
    exactly the quarter moon.
    """
    cos_p = math.cos(2 * math.pi * phase)
    waxing = phase < 0.5
    rx = abs(cos_p) * R
    top, bottom = f"{CX} {CY - R}", f"{CX} {CY + R}"

    limb_sweep = 1 if waxing else 0
    if waxing:
        term_sweep = 0 if cos_p > 0 else 1
    else:
        term_sweep = 1 if cos_p > 0 else 0

    return (f"M {top} A {R} {R} 0 0 {limb_sweep} {bottom} "
            f"A {rx:.2f} {R} 0 0 {term_sweep} {top} Z")


def draw(when: datetime) -> tuple[str, str, float]:
    phase = phase_of(when)
    lit = (1 - math.cos(2 * math.pi * phase)) / 2
    name = name_of(phase)

    # The glow follows the light, so a new moon does not blaze like a full one.
    # The unlit disc keeps a faint ashen face and rim, which is earthshine: the
    # sunlight Earth throws back onto the dark of the moon. Real, and it means
    # the banner never loses its anchor on the nights the crescent is a sliver.
    svg = (
        f'<!--moon-->'
        f'<circle cx="{CX}" cy="{CY}" r="70" fill="url(#moonGlow)" opacity="{0.3 + 0.7 * lit:.2f}"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{f.CREAM}" opacity="{0.20 - 0.12 * lit:.2f}"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{f.CREAM}" '
        f'stroke-width="0.8" opacity="{0.35 - 0.25 * lit:.2f}"/>'
        f'<path d="{lit_path(phase)}" fill="#f4f0ff"><title>{name}, {lit:.0%} lit</title></path>'
        f'<!--/moon-->'
    )
    return svg, name, lit


def main() -> int:
    when = datetime.now(timezone.utc)
    moon, name, lit = draw(when)

    svg = BANNER.read_text()
    patched, n = re.subn(r"<!--moon-->.*?<!--/moon-->", lambda _: moon, svg, flags=re.S)
    if not n:
        print("banner: no moon markers, leaving it alone", file=sys.stderr)
        return 1

    BANNER.write_text(patched)
    print(f"{BANNER}: {name}, {lit:.0%} lit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
