#!/usr/bin/env python3
"""Fetch the public contribution calendar for the profile repository owner."""

from __future__ import annotations

from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
USERNAME = "Veeru19252"
OUTPUT = ROOT / "data" / "contributions.json"


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict[str, object]] = []
        self._current: dict[str, object] | None = None
        self._current_id: str | None = None
        self._cell_depth = 0
        self._text: list[str] = []
        self._days_by_id: dict[str, dict[str, object]] = {}
        self._tooltip_day: dict[str, object] | None = None
        self._tooltip_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "td" and attributes.get("data-date"):
            try:
                date.fromisoformat(attributes["data-date"] or "")
            except ValueError:
                return
            self._current = {
                "date": attributes["data-date"],
                "level": int(attributes.get("data-level") or 0),
            }
            self._current_id = attributes.get("id")
            self._cell_depth = 1
            self._text = []
        elif self._current is not None and tag == "td":
            self._cell_depth += 1
        elif tag == "tool-tip":
            self._tooltip_day = self._days_by_id.get(attributes.get("for") or "")
            self._tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self._tooltip_day is not None:
            self._tooltip_text.append(data)
        elif self._current is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip_day is not None:
            description = " ".join(self._tooltip_text)
            match = re.search(r"(\d[\d,]*)\s+contributions?", description)
            self._tooltip_day["count"] = int(match.group(1).replace(",", "")) if match else 0
            self._tooltip_day = None
            self._tooltip_text = []
            return
        if self._current is None or tag != "td":
            return
        self._cell_depth -= 1
        if self._cell_depth > 0:
            return

        self._current["count"] = 0
        self.days.append(self._current)
        if self._current_id:
            self._days_by_id[self._current_id] = self._current
        self._current = None
        self._current_id = None
        self._text = []


def main() -> None:
    url = f"https://github.com/users/{USERNAME}/contributions"
    request = Request(url, headers={"User-Agent": "profile-readme-contribution-calendar"})
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as error:
        raise SystemExit(f"Could not fetch {url}: {error}") from error

    parser = ContributionParser()
    parser.feed(page)
    if not parser.days:
        raise SystemExit("GitHub returned no contribution calendar cells; leaving existing data unchanged.")

    parser.days.sort(key=lambda item: str(item["date"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps({"username": USERNAME, "days": parser.days}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(parser.days)} contribution days to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
