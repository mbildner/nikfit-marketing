# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2"]
# ///
"""Render Nikfit public-site preview pages to static HTML.

Run from repo root:  uv run public_site/render.py
Output is served by the FastAPI app at /demo/ (see app/main.py).
"""
from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TPL = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "out"

env = Environment(
    loader=FileSystemLoader(TPL),
    autoescape=select_autoescape(["html"]),
)

schedule_preview = [
    {"day": "Mon", "time": "6:30a", "name": "HIIT", "tag": "Group", "tag_key": "hiit"},
    {"day": "Mon", "time": "9:30a", "name": "Pre/Postnatal", "tag": "Small group", "tag_key": "pre"},
    {"day": "Tue", "time": "12:00p", "name": "Strength", "tag": "Small group", "tag_key": "strength"},
    {"day": "Wed", "time": "6:30a", "name": "HIIT", "tag": "Group", "tag_key": "hiit"},
    {"day": "Thu", "time": "6:30p", "name": "Strength", "tag": "Group", "tag_key": "strength"},
    {"day": "Sat", "time": "8:00a", "name": "Strength", "tag": "Group", "tag_key": "strength"},
]

testimonials = [
    {
        "quote": "I quit every workout program I've ever started except this one. Nikki was the first trainer who actually listened when I said my back was a mess. Six months in, my back is the strongest it's been since college.",
        "name": "Sarah K.",
        "town": "Cresskill",
    },
    {
        "quote": "I worked with Nikki through both of my pregnancies. She knows exactly when to push and when to back off. I came back to the same body weight twice but felt three times stronger.",
        "name": "Maya R.",
        "town": "Tenafly",
    },
]

days = [
    {"name": "Monday", "sessions": [
        {"time": "6:30 am", "name": "HIIT", "note": "Group · drop-in with a heads up"},
        {"time": "9:30 am", "name": "Pre/Postnatal", "note": "Small group · 6 max"},
        {"time": "11:00 am", "name": "1-on-1 slots", "note": "Booked via inquiry"},
        {"time": "6:30 pm", "name": "Strength", "note": "Group · drop-in with a heads up"},
    ]},
    {"name": "Tuesday", "sessions": [
        {"time": "7:00 am", "name": "1-on-1 slots", "note": "Booked via inquiry"},
        {"time": "12:00 pm", "name": "Strength", "note": "Small group · 6 max"},
        {"time": "6:30 pm", "name": "1-on-1 slots", "note": "Booked via inquiry"},
    ]},
    {"name": "Wednesday", "sessions": [
        {"time": "6:30 am", "name": "HIIT", "note": "Group · drop-in with a heads up"},
        {"time": "9:30 am", "name": "Pre/Postnatal", "note": "Small group · 6 max"},
        {"time": "6:30 pm", "name": "Strength", "note": "Group · drop-in with a heads up"},
    ]},
    {"name": "Thursday", "sessions": [
        {"time": "7:00 am", "name": "1-on-1 slots", "note": "Booked via inquiry"},
        {"time": "12:00 pm", "name": "Strength", "note": "Small group · 6 max"},
        {"time": "6:30 pm", "name": "HIIT", "note": "Group · drop-in with a heads up"},
    ]},
    {"name": "Friday", "sessions": [
        {"time": "6:30 am", "name": "HIIT", "note": "Group · drop-in with a heads up"},
        {"time": "9:30 am", "name": "Pre/Postnatal", "note": "Small group · 6 max"},
        {"time": "11:00 am", "name": "1-on-1 slots", "note": "Booked via inquiry"},
    ]},
    {"name": "Saturday", "sessions": [
        {"time": "8:00 am", "name": "Strength", "note": "Group · drop-in with a heads up"},
        {"time": "9:30 am", "name": "Small group blend", "note": "Small group · 8 max"},
    ]},
    {"name": "Sunday", "sessions": []},
]

PAGES = {
    "index.html": {
        "page": "home",
        "schedule_preview": schedule_preview,
        "testimonials": testimonials,
    },
    "schedule.html": {
        "page": "schedule",
        "week_of": "May 25",
        "days": days,
    },
    "inquire.html": {
        "page": "inquire",
    },
    "thanks.html": {
        "page": "inquire",
    },
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, ctx in PAGES.items():
        rendered = env.get_template(name).render(**ctx)
        (OUT / name).write_text(rendered)
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    print(f"Rendered {len(PAGES)} pages to {OUT}")
    print(f"  → file://{(OUT / 'index.html').resolve()}")


if __name__ == "__main__":
    main()
