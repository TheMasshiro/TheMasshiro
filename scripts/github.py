"""Thin GitHub reads for the profile cards.

The contribution calendar is taken from the public contributions fragment
rather than GraphQL, because the token Actions hands a workflow cannot read
user contribution data and asking people to mint a PAT to see their own
squares is a bad trade.
"""

import json
import os
import re
import urllib.request

API = "https://api.github.com"
UA = "frieren-profile"


def _get(url: str, accept: str = "application/vnd.github+json") -> str:
    headers = {"User-Agent": UA, "Accept": accept}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode()


def user(login: str) -> dict:
    return json.loads(_get(f"{API}/users/{login}"))


def repos(login: str) -> list[dict]:
    out, page = [], 1
    while True:
        batch = json.loads(_get(f"{API}/users/{login}/repos?per_page=100&page={page}"))
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def language_bytes(login: str, owned: list[dict]) -> dict[str, int]:
    """Bytes per language across the user's own repositories."""
    totals: dict[str, int] = {}
    for repo in owned:
        if repo.get("fork"):
            continue
        for lang, size in json.loads(_get(repo["languages_url"])).items():
            totals[lang] = totals.get(lang, 0) + size
    return dict(sorted(totals.items(), key=lambda kv: -kv[1]))


def search_count(query: str) -> int:
    kind = "commits" if query.startswith("commits:") else "issues"
    q = query.split(":", 1)[1]
    return json.loads(_get(f"{API}/search/{kind}?q={q}&per_page=1"))["total_count"]


CELL = re.compile(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*data-level="(\d)"')


def contributions(login: str) -> tuple[list[tuple[str, int]], int]:
    """(date, level) for the trailing year, plus the headline total.

    Levels run 0 to 4 and are the only per-day signal the fragment exposes,
    which is enough to decide whether a day counts and how tall to draw it.
    """
    html = _get(f"https://github.com/users/{login}/contributions", "text/html")
    days = sorted((d, int(lvl)) for d, lvl in CELL.findall(html))
    if not days:
        # Better a red cross on the run than a card quietly going stale.
        raise RuntimeError(f"no contribution cells for {login}; the markup moved")
    headline = re.search(r"([\d,]+)\s+contributions?\s+in", html)
    return days, int(headline.group(1).replace(",", "")) if headline else 0


def streaks(days: list[tuple[str, int]]) -> tuple[int, int]:
    """(current, longest) runs of days with any activity."""
    longest = run = 0
    for _, level in days:
        run = run + 1 if level else 0
        longest = max(longest, run)

    # A run only counts as current if it reaches today, or yesterday when
    # today has not been counted yet. An earlier run is history, not a streak.
    current = 0
    for age, (_, level) in enumerate(reversed(days)):
        if not level:
            if age == 0:
                continue
            break
        current += 1
    return current, longest
