# nikfit-marketing

Static marketing site for Nikfit (`nik.fit`). Hosted on Netlify, deployed from `main`.

## Structure

Everything Netlify serves lives under `site/` — one directory, no templating, no build step. Each HTML page is fully self-contained; shared chrome (nav, footer, SEO meta, fonts) is duplicated across pages rather than abstracted, since the page count is small and edits go through Claude (which can keep them in sync with one prompt).

```
site/
├── index.html         home: hero, "what people say", CTAs
├── schedule.html      weekly schedule
├── inquire.html       inquiry form (Netlify Forms)
├── thanks.html        post-submission landing (noindex)
├── style.css
├── inquiry-validator.js
├── phone-format.js
├── favicon.svg
├── og-image.jpg
├── robots.txt
└── sitemap.xml
```

## Editing

Two ways to edit:

1. **Via nikfit's MCP editor** (claude.ai → connector at `https://nikfit.fly.dev/admin/marketing/mcp`). Each tool call commits to a working clone of this repo. Clicking Deploy at `https://nikfit.fly.dev/admin/marketing` pushes pending commits to GitHub; Netlify auto-builds.

2. **Hand-edit on a branch** via `git`. PR + merge to main; Netlify auto-deploys.

## Quality tooling (one-time setup)

```bash
uv tool install pre-commit   # or: brew install pre-commit
pre-commit install           # wires up the git pre-commit hook
```

Hooks: file hygiene, `ruff check`, `gitleaks`, `yarn test`.

```bash
git commit --no-verify   # emergency bypass — justify in commit message
```

## Deploy

Push to `main`. Netlify auto-deploys `site/` within ~30 seconds.

```bash
netlify deploy --prod   # optional manual deploy
netlify dev             # local preview with Netlify Forms emulation
```

## Form submissions

The inquiry form has `data-netlify="true"`. Submissions appear in:
- Netlify dashboard → Forms → "inquiry"
- Email notifications (configured in dashboard)

Spam protection: honeypot field (`company`) + Akismet.

## Netlify config (CI)

`netlify-config.json` declares the desired Netlify state (form submission
notifications, etc.). `scripts/configure_netlify.py` runs in CI on every push
to `main` and **creates missing resources only**. It never updates, deletes,
or re-enables existing ones — so disabling a notification via dashboard sticks.

One-time setup of state that isn't enforced by CI (initial bootstrap):

```bash
# Allow form detection (Netlify defaults this to true on some sites, which
# silently breaks data-netlify form processing).
netlify api updateSite --data '{"site_id":"<site_id>","body":{"processing_settings":{"ignore_html_forms":false,"html":{"pretty_urls":true}}}}'
```

CI requires the `NETLIFY_AUTH_TOKEN` repo secret. Create a PAT at
https://app.netlify.com/user/applications#personal-access-tokens, then:

```bash
gh secret set NETLIFY_AUTH_TOKEN -R mbildner/nikfit-marketing
```

## Pre-launch private review gate

`netlify/edge-functions/basic-auth.ts` is an HTTP Basic Auth gate. It's a **no-op by default**. To turn it on:

```bash
netlify env:set BASIC_AUTH_USER nikki
netlify env:set BASIC_AUTH_PASSWORD <a-real-password>
```

To turn it off before launch, unset both vars or delete the file:

```bash
netlify env:unset BASIC_AUTH_USER
netlify env:unset BASIC_AUTH_PASSWORD
```
