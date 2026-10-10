"""Thin GitHub reads for the profile cards.

Contributions come from GraphQL when GH_TOKEN holds a personal access token,
because that is the only way to count private contributions: a logged-out
visitor sees roughly two thirds of the real activity here, and the Actions
token cannot read contributions at all. Without a PAT it falls back to the
public fragment, which undercounts but needs no secret.
"""

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

API = "https://api.github.com"
UA = "frieren-profile"


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Let a local run pick up GH_TOKEN without exporting it by hand.

    Real environment variables win, so Actions secrets are never shadowed by a
    stale file someone forgot about.
    """
    try:
        text = path.read_text()
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("\"'")
        if value:
            os.environ.setdefault(key.strip(), value)


_load_dotenv()


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


GRAPHQL = "https://api.github.com/graphql"

CALENDAR = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      restrictedContributionsCount
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""


def _graphql(token: str, doc: str, **variables):
    body = json.dumps({"query": doc, "variables": variables}).encode()
    req = urllib.request.Request(GRAPHQL, data=body, headers={
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": UA,
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "graphql error"))
    return payload["data"]


def _grade(counts: list[int]):
    """Map a day's count onto GitHub's five shades, by quartile of active days."""
    active = sorted(c for c in counts if c > 0)
    if not active:
        return lambda _: 0
    cuts = [active[min(int(len(active) * f), len(active) - 1)] for f in (0.25, 0.5, 0.75)]

    def level(count: int) -> int:
        if count <= 0:
            return 0
        return 1 + sum(count > cut for cut in cuts)
    return level


def _contributions_graphql(login: str, token: str):
    today = date.today()
    start = today - timedelta(days=364)
    collection = _graphql(
        token, CALENDAR, login=login,
        **{"from": f"{start}T00:00:00Z", "to": f"{today}T23:59:59Z"},
    )["user"]["contributionsCollection"]

    calendar = collection["contributionCalendar"]
    counted = [(d["date"], d["contributionCount"])
               for week in calendar["weeks"] for d in week["contributionDays"]]
    level = _grade([c for _, c in counted])
    return (sorted((day, level(c)) for day, c in counted),
            calendar["totalContributions"],
            collection["restrictedContributionsCount"])


CELL = re.compile(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*data-level="(\d)"')


def _contributions_public(login: str) -> tuple[list[tuple[str, int]], int]:
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


def contributions(login: str) -> tuple[list[tuple[str, int]], int]:
    """(date, level) for the trailing year, plus the total.

    A PAT in GH_TOKEN includes private contributions. Anything else sees only
    what a logged-out visitor sees, which is a real undercount, so say so.
    """
    pat = os.environ.get("GH_TOKEN")
    if pat:
        try:
            days, total, private = _contributions_graphql(login, pat)
            print(f"contributions: {total:,} via graphql ({private:,} private)")
            return days, total
        except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as exc:
            print(f"contributions: graphql unavailable ({exc}), using public view")

    days, total = _contributions_public(login)
    print(f"contributions: {total:,} public only; private ones are not counted. "
          f"Set GH_TOKEN to a PAT with read:user, or turn on "
          f"'Include private contributions on my profile' in GitHub settings.")
    return days, total


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
