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
