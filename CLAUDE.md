# CLAUDE.md

Orientation for Claude sessions working in this repo. For architecture and
operational deep-dives, read `README.md`. This file covers the things that
are easy to get wrong if you assume a normal solo-dev workflow.

## What this repo is

nikfit-marketing — the public marketing site for NikFit (`nik.fit`).
Separate repo from the main `nikfit` app (which is the admin tool for
managing clients, packages, attendance, etc.). This site is what
prospective clients see: hero, services, schedule, inquiry form.

Stack: Jinja2 templates rendered to static HTML by `render.py` (the `out/`
directory is committed and is what Netlify actually serves — there is no
build step on Netlify). Plain CSS, no JS framework. Netlify Forms handles
inquiry submissions (no backend). Optional Basic Auth edge function for
pre-launch private review. Architecture, Netlify config workflow, form
spam protection, and the pre-launch gate are all in `README.md`.

Layout at a glance: `templates/` holds the Jinja sources; `render.py`
walks them into `out/`; `static/` is copied as-is; `tests/` is Node
`--test` JS unit tests (e.g. phone-format); `scripts/` has ops helpers
(`configure_netlify.py`); `netlify/edge-functions/` holds the optional
Basic Auth gate.

## You are not the only Claude in here

Moshe is the **solo human dev**, but he runs **many parallel Claude sessions
in `git worktree`s** across his projects. From your point of view that
means there are *other agents* working on the same repo at the same time.
Concretely:

- `origin/main` may have moved since this session started. Another session
  may have merged a PR or pushed directly to main while you were thinking.
- A file you read 20 minutes ago in your worktree may have been edited by a
  sibling session in a different worktree. Re-Read before you Edit if any
  meaningful time has passed or if the area is hot (templates, render.py,
  inquiry form markup, Netlify config).
- Don't `git worktree prune` aggressively or delete unfamiliar worktrees —
  they may belong to a sibling session.

### Required pre-push dance

Before pushing **any** branch, do this — don't skip steps even on a
"trivial" change:

1. `git fetch origin` — get the current state of main and your branch.
2. Compare `HEAD` to `origin/main`. If `origin/main` has new commits since
   you branched, **rebase** onto it (`git rebase origin/main`). Don't merge.
3. Resolve any conflicts thoughtfully. A conflict usually means a sibling
   session touched the same surface — read both sides before picking.
4. Re-run the checks **after** the rebase, not just before — `uv run
   render.py` (so `out/` matches), `uvx ruff@0.15.5 check .`, and `yarn
   test`. The rebase may have silently combined incompatible changes that
   both passed in isolation. The render-check CI job is unforgiving about
   a stale `out/`.
5. Push only if green. `main` auto-deploys to Netlify within ~10 seconds,
   so a bad push ships to prod.

If you find yourself about to `git push --force` or `--force-with-lease`,
stop and confirm with Moshe first. Force-pushing a shared branch can clobber
work from a sibling session that has been collaborating on the same branch.

### Don't trust your cached view of "main"

When you read commit history, branch state, or file contents at the *start*
of a long session, that snapshot can be stale by the time you act on it.
Re-fetch and re-check before any push, PR creation, or recommendation that
depends on "what's on main right now."

## Tickets and branches (mandatory)

Every commit must be associated with a **Jira ticket** in project `NIKFIT`
(workspace `corklight.atlassian.net`). This repo is part of the NIKFIT
GTM/public-site effort — see the `project_nikfit_gtm` auto-memory for the
active epic/ticket structure. The ticket is *why* the change is being
made — it's the durable record that future Claude sessions (and future
Moshe) read to understand intent.

**Rules:**

- **Branch name = ticket key.** Use `NIKFIT-123` as the branch name, not
  `feat/NIKFIT-123-thing` or `fix/whatever`. The bare key is the branch.
- **Commit subject ends with the ticket key in parentheses.** Example:
  `Add HTML5 pattern validation to inquiry phone + email fields (NIKFIT-7)`.
  Multiple tickets: `(NIKFIT-4, NIKFIT-7)`.
- **No ticket → no commit.** If there isn't a ticket for the work yet,
  create one (or ask Moshe to point at the right one) before writing code.
  The ticket should describe the *problem* or *goal*, not just restate the
  diff.
- Existing legacy commits in this repo predate the convention. Don't
  rewrite history to add keys — apply the rule to new work going forward.

When you don't know which ticket applies, **ask** rather than inventing one
or omitting it. Inventing a key (e.g. `NIKFIT-999`) is worse than no key.

## The check gate

Pre-commit hooks and CI run the same set of checks. Both must pass before
a push lands a deploy.

Pre-commit (see `.pre-commit-config.yaml`):
- file hygiene (trailing whitespace, EOL, JSON/YAML/TOML syntax, max file size)
- `ruff check` (lint + bandit-style security checks)
- `gitleaks` (refuse committed secrets)
- render-check (`out/` matches templates after re-render)

CI (`.github/workflows/ci.yml`) runs the same lint + secret scan + render
check, plus `yarn test` for the JS unit tests, plus
`scripts/configure_netlify.py` on pushes to `main` to sync Netlify state.

Local commands:
- `uv run render.py` — rebuild `out/` from templates. Run this any time
  you touch `templates/` or `static/`, then commit the regenerated `out/`.
- `yarn test` — run the Node `--test` JS unit tests.
- `pre-commit run --all-files` — sanity check after pulling.
- `netlify dev` — local preview with Netlify Forms emulation.

Don't `--no-verify` to bypass a failing hook unless Moshe explicitly
approves it — the hook caught something real. If you must bypass for an
emergency, justify it in the commit message.

## When in doubt

- Architecture / how a piece works → `README.md`
- Netlify config drift / what CI enforces → `scripts/configure_netlify.py`
  and `netlify-config.json`
- Active GTM scope and ticket structure → `project_nikfit_gtm` auto-memory
  (or browse Jira NIKFIT directly)
- Existing conventions Moshe has confirmed → check git log for recent
  commits in the area you're editing; the commit messages are dense and
  intentional.
