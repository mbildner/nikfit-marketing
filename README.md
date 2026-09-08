# nikfit-marketing

Static one-page site for **Nikfit** — Nikki Bildner's private women's personal
training studio in Teaneck, NJ. Served from **GitHub Pages** at nik.fit.

No build step, no framework — the files at the repo root are what gets served.
Booking is a `sms:` "text me" link to (201) 705-2307 (no forms/backend).

```
index.html         the business card (hero, services, CTA)
schedule.html      redirect -> /  (old Apply URL)
style.css          Nikfit teal/mauve palette
headshot-round.png circular hero portrait  (cutout master: headshot-cutout.png)
og-image.jpg  favicon.svg  robots.txt  sitemap.xml  .nojekyll
```

## Run locally
```bash
python3 -m http.server 8080   # http://localhost:8080
```

## Deploy
Push to `main`; GitHub Pages redeploys automatically. Custom domain nik.fit is
set via a `CNAME` file (added at DNS cutover) + registrar DNS; GitHub auto-HTTPS.
