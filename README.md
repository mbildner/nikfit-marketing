# nikfit-marketing

Static marketing site for Nikfit (`nik.fit`). Hosted on Netlify, deployed from `main`.

## Stack

- Jinja2 templates → static HTML (no build step on Netlify; `out/` is committed)
- Plain CSS, no JS framework
- Netlify Forms handles the inquiry submission (no backend)

## Local dev

```bash
uv run render.py        # rebuild out/
open out/index.html     # preview
```

## Deploy

Push to `main`. Netlify auto-deploys `out/` within ~10 seconds.

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
