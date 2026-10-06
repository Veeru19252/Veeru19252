#!/usr/bin/env python3
"""Render self-contained animated SVG art for the profile README."""

from __future__ import annotations

from datetime import date, timedelta
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "contributions.json"
PALETTE = ("#e8edf0", "#b8e3d0", "#72c7a2", "#31976c", "#17613f")


def read_days() -> list[dict[str, object]]:
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    normalized = []
    for item in days:
        parsed_date = date.fromisoformat(str(item["date"]))
        count = max(0, int(item.get("count", 0)))
        level = max(0, min(4, int(item.get("level", 0))))
        if count and level == 0:
            level = min(4, 1 + count.bit_length() // 2)
        normalized.append({"date": parsed_date, "count": count, "level": level})
    return sorted(normalized, key=lambda item: item["date"])


def streaks(days: list[dict[str, object]]) -> tuple[int, int, int]:
    total = sum(int(item["count"]) for item in days)
    longest = 0
    run = 0
    previous: date | None = None
    counts_by_date = {item["date"]: int(item["count"]) for item in days}
    for item in days:
        current = item["date"]
        if int(item["count"]) > 0:
            run = run + 1 if previous == current - timedelta(days=1) else 1
            longest = max(longest, run)
        else:
            run = 0
        previous = current

    current_streak = 0
    cursor = max(counts_by_date, default=date.today())
    while counts_by_date.get(cursor, 0) > 0:
        current_streak += 1
        cursor -= timedelta(days=1)
    return total, current_streak, longest


def render_ascii() -> str:
    art = (
        "  .----------------------.",
        "  |   .------------.     |",
        "  |   |  ________  |     |",
        "  |   | /  ____  \\ |     |",
        "  |   |/  /    \\  \\|     |",
        "  |   ||  | () |  ||     |",
        "  |   ||  \\____/  ||     |",
        "  |   |\\________/ |     |",
        "  |   |  _/____\\_  |     |",
        "  |   | /  /  \\  \\ |     |",
        "  |   |/__/    \\__\\|     |",
        "  |   '------------'     |",
        "  '----------------------'",
    )
    rows = []
    for index, line in enumerate(art):
        delay = index * 0.075
        rows.append(
            f'<text x="20" y="{42 + index * 22}" class="art">{html.escape(line)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" '
            'dur="0.28s" fill="freeze" /></text>'
        )
    rows.append(
        '<text x="20" y="365" class="caption">ASCII PROFILE ART / REPLACE WITH YOUR PORTRAIT'
        '<animate attributeName="opacity" from="0" to="1" begin="1.2s" '
        'dur="0.35s" fill="freeze" /></text>'
    )
    return """<svg xmlns="http://www.w3.org/2000/svg" width="370" height="390" viewBox="0 0 370 390">
<rect width="370" height="390" rx="8" fill="#101820"/>
<rect x="1" y="1" width="368" height="388" rx="8" fill="none" stroke="#34444b"/>
<circle cx="18" cy="18" r="4" fill="#f26b5b"/><circle cx="32" cy="18" r="4" fill="#e9bb55"/><circle cx="46" cy="18" r="4" fill="#67c587"/>
<text x="66" y="22" fill="#91a3a8" font-family="monospace" font-size="11">profile-art.svg</text>
<g fill="#a7d8c1" font-family="monospace" font-size="16" xml:space="preserve">""" + "\n".join(rows) + "\n</g>\n</svg>\n"


def render_info_card() -> str:
    rows = (
        ("ROLE", "Software Developer"),
        ("STACK", "C++23 / Python / Systems"),
        ("FOCUS", "Databases / Distributed Systems"),
        ("ALSO", "AI / ML projects"),
    )
    content = []
    for index, (label, value) in enumerate(rows):
        y = 112 + index * 62
        delay = 0.35 + index * 0.16
        content.append(
            f'<text x="30" y="{y}" class="key">{html.escape(label)}</text>'
            f'<text x="150" y="{y}" class="value">{html.escape(value)}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
            'dur="0.3s" fill="freeze" /></text>'
        )
    return """<svg xmlns="http://www.w3.org/2000/svg" width="490" height="390" viewBox="0 0 490 390">
<rect width="490" height="390" rx="8" fill="#f3f7f5"/>
<rect x="1" y="1" width="488" height="388" rx="8" fill="none" stroke="#bfd0c8"/>
<rect width="490" height="42" rx="8" fill="#20372f"/><path d="M0 34h490v8H0z" fill="#20372f"/>
<circle cx="18" cy="21" r="4" fill="#f26b5b"/><circle cx="32" cy="21" r="4" fill="#e9bb55"/><circle cx="46" cy="21" r="4" fill="#67c587"/>
<text x="66" y="25" fill="#e7f0eb" font-family="monospace" font-size="12">veeru@github: ~</text>
<text x="30" y="78" fill="#238157" font-family="monospace" font-size="16" font-weight="700">$ profile --summary</text>
<g font-family="monospace" font-size="13">
<path d="M30 91h430" stroke="#d2dfd8"/>""" + "\n".join(content) + """
</g>
<text x="30" y="365" fill="#667a71" font-family="monospace" font-size="11">Building things, one commit at a time.</text>
</svg>
"""


def render_heatmap(days: list[dict[str, object]]) -> str:
    total, current_streak, longest_streak = streaks(days)
    by_date = {item["date"]: item for item in days}
    if days:
        first_day = days[0]["date"]
        grid_start = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
        last_day = days[-1]["date"]
    else:
        last_day = date.today()
        grid_start = last_day - timedelta(days=370 + (last_day.weekday() + 1) % 7)
    week_count = min(53, max(1, ((last_day - grid_start).days // 7) + 1))
    cells = []
    months = []
    seen_months: set[tuple[int, int]] = set()
    for week in range(week_count):
        for weekday in range(7):
            current = grid_start + timedelta(days=week * 7 + weekday)
            if current > last_day:
                continue
            item = by_date.get(current)
            count = int(item["count"]) if item else 0
            level = int(item["level"]) if item else 0
            color = PALETTE[level]
            x = 48 + week * 14
            y = 38 + weekday * 14
            delay = (week + weekday) * 0.012
            title = f'{count} contributions on {current.isoformat()}'
            cells.append(
                f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" '
                f'fill="{color}" aria-label="{html.escape(title)}">'
                f'<title>{html.escape(title)}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.22s" fill="freeze" />'
                '</rect>'
            )
            month_key = (current.year, current.month)
            if current.day == 1 and month_key not in seen_months:
                months.append(
                    f'<text x="{x}" y="25" class="label">{current.strftime("%b")}</text>'
                )
                seen_months.add(month_key)

    grid_width = 48 + week_count * 14 + 8
    footer = (
        f"{total:,} contributions  |  current streak: {current_streak} days  |  "
        f"longest streak: {longest_streak} days"
    )
    legend = []
    for level, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{grid_width - 145 + level * 16}" y="151" width="11" height="11" '
            f'rx="2" fill="{color}" />'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="184" viewBox="0 0 860 184" role="img">
<rect width="860" height="184" rx="8" fill="#101820"/>
<rect x="1" y="1" width="858" height="182" rx="8" fill="none" stroke="#34444b"/>
<g class="label" font-family="monospace" font-size="10" fill="#91a3a8">{''.join(months)}</g>
<g font-family="monospace" font-size="9" fill="#91a3a8">
<text x="8" y="53">Mon</text><text x="8" y="81">Wed</text><text x="8" y="109">Fri</text>
</g>
<g>{''.join(cells)}</g>
<text x="48" y="164" fill="#91a3a8" font-family="monospace" font-size="10">Less</text>
{''.join(legend)}
<text x="{grid_width - 60}" y="160" fill="#91a3a8" font-family="monospace" font-size="10">More</text>
<text x="48" y="178" fill="#d4e1db" font-family="monospace" font-size="10">{html.escape(footer)}</text>
</svg>
"""


def main() -> None:
    days = read_days()
    (ROOT / "profile-ascii.svg").write_text(render_ascii(), encoding="utf-8")
    (ROOT / "info-card.svg").write_text(render_info_card(), encoding="utf-8")
    (ROOT / "contrib-heatmap.svg").write_text(render_heatmap(days), encoding="utf-8")
    print("Rendered profile-ascii.svg, info-card.svg, and contrib-heatmap.svg")


if __name__ == "__main__":
    main()
