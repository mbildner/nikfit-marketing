#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bootstrap Netlify site config from netlify-config.json. Idempotent.

Only creates resources that are missing — never updates or re-enables
existing ones. This avoids fighting deliberate dashboard changes
(e.g. disabling an email notification you no longer want).

Locally:   uv run scripts/configure_netlify.py
In CI:     NETLIFY_AUTH_TOKEN=<pat> python3 scripts/configure_netlify.py

If NETLIFY_AUTH_TOKEN is not set, falls back to the local netlify-cli
session token at ~/.config/netlify/config.json. Exits non-zero on any
API error or if no token is available.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.netlify.com/api/v1"
ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "netlify-config.json"


def get_token() -> str:
    tok = os.environ.get("NETLIFY_AUTH_TOKEN")
    if tok:
        return tok
    cli_cfg = Path.home() / ".config" / "netlify" / "config.json"
    if cli_cfg.exists():
        data = json.loads(cli_cfg.read_text())
        for user in data.get("users", {}).values():
            tok = user.get("auth", {}).get("token")
            if tok:
                return tok
    sys.exit(
        "No Netlify auth available. Set NETLIFY_AUTH_TOKEN or run `netlify login`."
    )


TOKEN = get_token()


ROTATION_RUNBOOK = "https://corklight.atlassian.net/browse/NIKFIT-13"


def api(method: str, path: str, body: dict | None = None) -> dict | list:
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    # URL is constructed from API_BASE (constant) + path (only ever called
    # with literal strings inside this script); never tainted at runtime.
    req = urllib.request.Request(url, data=data, method=method, headers=headers)  # noqa: S310
    try:
        with urllib.request.urlopen(req) as resp:  # noqa: S310
            txt = resp.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()
        except Exception:
            err_body = "<unreadable>"
        if e.code == 401:
            sys.exit(
                f"::error::Netlify API returned 401. The NETLIFY_AUTH_TOKEN "
                f"PAT is almost certainly expired or revoked.\n\n"
                f"Rotation runbook: {ROTATION_RUNBOOK}\n\n"
                f"Raw response: {err_body}"
            )
        sys.exit(f"API error {e.code} on {method} {path}: {err_body}")


def hook_matches(existing: dict, desired: dict) -> bool:
    if existing.get("type") != desired["type"]:
        return False
    if existing.get("event") != desired["event"]:
        return False
    return existing.get("data") == desired["data"]


def ensure_form_notifications(site_id: str, desired_hooks: list[dict]) -> list[str]:
    """Create missing hooks. Leave existing hooks alone (even if disabled)."""
    existing = api("GET", f"/hooks?site_id={site_id}")
    if not isinstance(existing, list):
        raise TypeError(f"GET /hooks expected list, got {type(existing).__name__}")
    submission_hooks = [
        h for h in existing if h.get("event") == "submission_created"
    ]
    changes: list[str] = []
    for desired in desired_hooks:
        found = next(
            (h for h in submission_hooks if hook_matches(h, desired)), None
        )
        if found:
            continue
        body = {"site_id": site_id, **desired}
        api("POST", f"/hooks?site_id={site_id}", body)
        label = desired.get("data", {}).get("email") or "<no-email>"
        changes.append(
            f"created hook {desired['type']}/{desired['event']} -> {label}"
        )
    return changes


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text())
    site_id = config["site_id"]
    changes: list[str] = []
    changes += ensure_form_notifications(site_id, config.get("form_notifications", []))
    if changes:
        print("Applied changes:")
        for c in changes:
            print(f"  - {c}")
    else:
        print("Netlify config already in sync (no missing resources).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
