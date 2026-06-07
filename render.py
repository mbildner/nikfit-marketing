# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2"]
# ///
"""Render Nikfit public-site preview pages to static HTML.

Run from repo root:  uv run public_site/render.py
Output is served by the FastAPI app at /demo/ (see app/main.py).
"""
from __future__ import annotations

import argparse
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
        "quote": "At my daughter's suggestion, I started working with Nikki six years ago and haven't stopped since. No two workouts are identical - she keeps things fresh and adapts to my evolving needs, always challenging me to reach new goals while encouraging me in the most positive way. I call her my 'fitness coach' because she is so much more than a personal trainer.",
        "name": "Ronit H.",
        "town": "Teaneck",
    },
    {
        "quote": "Taking classes with Nikki has been an absolute blast. Every class challenges me in the best way, pushing me beyond what I thought I could do while still making it fun and empowering. I leave feeling stronger, more energized, and proud of what my body can accomplish. Nikki has created something really special and I'm so grateful to be a part of it.",
        "name": "Denise F.",
        "town": "Teaneck",
    },
    {
        "quote": "Working out has never been a hobby of mine until I met Nikki. She's fantastic! I've been going to personal trainers for years and always dreaded the sessions. Now I'm always eager and excited. Nikki empowers you while making you feel like you can do anything. I do both private training and group Pilates and they're both so much fun. I gave birth to my third baby in August and was looking to tone up my post-baby body. Nikki is the best at what she does. Give her a shot, you won't be disappointed.",
        "name": "Jordana S.",
        "town": "Teaneck",
    },
]

days = [
    {"name": "Monday", "sessions": [
        {"time": "2:30 pm", "name": "1-on-1 Personal Training", "note": "Booked via inquiry"},
    ]},
    {"name": "Tuesday", "sessions": [
        {"time": "12:00 pm", "name": "Strength Training", "note": "Small group · 4 max"},
        {"time": "2:30 pm", "name": "1-on-1 Personal Training", "note": "Booked via inquiry"},
    ]},
    {"name": "Wednesday", "sessions": [
        {"time": "11:00 am", "name": "1-on-1 Personal Training", "note": "Booked via inquiry"},
        {"time": "1:00 pm", "name": "1-on-1 Personal Training", "note": "Booked via inquiry"},
    ]},
    {"name": "Friday", "sessions": [
        {"time": "10:00 am", "name": "Pilates Sculpt", "note": "Small group · 4 max"},
        {"time": "11:15 am", "name": "HIIT", "note": "Small group · 4 max"},
    ]},
]

SITE_URL = "https://nik.fit"

PAGES = {
    "index.html": {
        "page": "home",
        "description": "Private personal training studio in Teaneck, NJ. 1-on-1 training and small-group Strength, Pilates Sculpt, and HIIT for women. Postnatal recovery and body-confidence programs.",
        "canonical": f"{SITE_URL}/",
        "schedule_preview": schedule_preview,
        "testimonials": testimonials,
    },
    "schedule.html": {
        "page": "schedule",
        "description": "This week's small-group and 1-on-1 schedule at Nikfit in Teaneck, NJ. 4-person cap on group classes; send an inquiry to claim a spot.",
        "canonical": f"{SITE_URL}/schedule.html",
        "week_of": "June 1",
        "days": days,
    },
    "inquire.html": {
        "page": "inquire",
        "description": "Inquire about personal training, small-group classes, or pre/postnatal coaching at Nikfit in Teaneck, NJ. Nikki replies within a day.",
        "canonical": f"{SITE_URL}/inquire.html",
    },
    "thanks.html": {
        "page": "inquire",
        "description": "Thanks for your inquiry. Nikki replies within a day.",
        "canonical": f"{SITE_URL}/thanks.html",
        "noindex": True,
    },
}


def main(dev: bool = False) -> None:
    OUT.mkdir(exist_ok=True)
    for name, ctx in PAGES.items():
        rendered = env.get_template(name).render(dev=dev, **ctx)
        (OUT / name).write_text(rendered)
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    shutil.copy(STATIC / "inquiry-validator.js", OUT / "inquiry-validator.js")
    shutil.copy(STATIC / "phone-format.js", OUT / "phone-format.js")
    shutil.copy(STATIC / "og-image.jpg", OUT / "og-image.jpg")
    shutil.copy(STATIC / "robots.txt", OUT / "robots.txt")
    shutil.copy(STATIC / "sitemap.xml", OUT / "sitemap.xml")
    if dev:
        shutil.copy(STATIC / "livereload.js", OUT / "livereload.js")
    print(f"Rendered {len(PAGES)} pages to {OUT} (dev={dev})")
    print(f"  → file://{(OUT / 'index.html').resolve()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dev", action="store_true", help="Inject live-reload script for local dev")
    args = ap.parse_args()
    main(dev=args.dev)
