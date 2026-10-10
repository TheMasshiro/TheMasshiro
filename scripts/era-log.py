#!/usr/bin/env python3
"""Draw the Era Log: how long the journey has run, and how little that is.

Frieren measures a decade the way everyone else measures an afternoon, so the
card states the elapsed time plainly and then undercuts it.

Deliberately accurate only to the month. An earlier version printed a day
count, which meant the file changed on every nightly run and CI committed it,
quietly padding the contribution graph with work nobody did. On a page arguing
that small honest steps add up, that was the wrong trade.
"""

import json
import os
import random
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frieren as f

W, H = 1000, 250
OUT = Path("profile/era.svg")

# Used when the API cannot be reached or the token cannot see contributions.
FALLBACK_START = date(2024, 1, 31)
GRAPHQL = "https://api.github.com/graphql"


def query(token: str, doc: str, **variables):
    body = json.dumps({"query": doc, "variables": variables}).encode()
    req = urllib.request.Request(
        GRAPHQL, data=body,
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "frieren-profile"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "graphql error"))
    return payload["data"]


def first_contribution(login: str, token: str) -> date:
    """The earliest day the calendar shows any activity."""
    years = query(token, """
        query($login:String!){ user(login:$login){
          contributionsCollection{ contributionYears } } }
    """, login=login)["user"]["contributionsCollection"]["contributionYears"]

    earliest = min(years)
    weeks = query(token, """
        query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
          contributionsCollection(from:$from,to:$to){
            contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }
    """, login=login,
        **{"from": f"{earliest}-01-01T00:00:00Z", "to": f"{earliest}-12-31T23:59:59Z"},
    )["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    days = [d for w in weeks for d in w["contributionDays"] if d["contributionCount"]]
    return date.fromisoformat(min(d["date"] for d in days))


def journey_start() -> date:
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", "TheMasshiro")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return FALLBACK_START
    try:
        return first_contribution(login, token)
    except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as exc:
        # The default Actions token usually cannot read user contributions. A
        # PAT in GH_TOKEN lifts this; until then the known date is fine.
        print(f"era-log: falling back to {FALLBACK_START} ({exc})", file=sys.stderr)
        return FALLBACK_START


def elapsed(start: date, today: date) -> tuple[int, int]:
    months = (today.year - start.year) * 12 + (today.month - start.month)
    if today.day < start.day:
        months -= 1
    return months // 12, months % 12


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
    start = journey_start()
    years, months = elapsed(start, date.today())

    parts = [plural(years, "year")] if years else []
    parts.append(plural(months, "month"))
    span = ", ".join(parts)
    started = start.strftime("%d %B %Y").lstrip("0")

    body = f'''<g class="fade">
{f.heading(W, "The Era Log", "HOW LONG THE JOURNEY HAS RUN", rule_y=106)}
<text x="500" y="158" text-anchor="middle" font-family="{f.SERIF}" font-size="40" font-style="italic" fill="{f.MINT}" filter="url(#glow)">{span}</text>
<text x="500" y="186" text-anchor="middle" font-family="{f.SERIF}" font-size="12" letter-spacing="1" fill="{f.MUTED}">since {started}</text>
<text x="500" y="220" text-anchor="middle" font-family="{f.SERIF}" font-size="15" font-style="italic" fill="{f.GOLD}" opacity="0.9">{undercut(years)}</text>
</g>'''

    # Seeded by the month so the drawing is stable until the month turns.
    OUT.write_text(f.card(W, H, body, mote_count=6,
                          rng=random.Random(years * 12 + months)))
    print(f"{OUT}: {span} since {started}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
