# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2"]
# ///
"""Render Nikfit public-site to static HTML.

Each template under templates/ owns its own metadata via {% set %} at the
top (description, canonical, breadcrumb, etc.) and inlines its content.
There is no Python data layer — content lives in HTML so it can be edited
directly via a file-CRUD MCP tool or hand-edits.

Templates starting with `_` are partials/macros and are not rendered as
pages.

Run from repo root:  uv run render.py
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

STATIC_FILES = [
    "style.css",
    "inquiry-validator.js",
    "phone-format.js",
    "og-image.jpg",
    "robots.txt",
    "sitemap.xml",
    "favicon.svg",
]


def main(dev: bool = False) -> None:
    OUT.mkdir(exist_ok=True)
    pages = sorted(p.name for p in TPL.glob("*.html") if not p.name.startswith("_"))
    for name in pages:
        rendered = env.get_template(name).render(dev=dev)
        (OUT / name).write_text(rendered)
    for f in STATIC_FILES:
        shutil.copy(STATIC / f, OUT / f)
    if dev:
        shutil.copy(STATIC / "livereload.js", OUT / "livereload.js")
    print(f"Rendered {len(pages)} pages to {OUT} (dev={dev})")
    print(f"  → file://{(OUT / 'index.html').resolve()}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dev", action="store_true", help="Inject live-reload script for local dev")
    args = ap.parse_args()
    main(dev=args.dev)
