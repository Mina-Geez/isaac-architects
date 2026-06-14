# Isaac Architects — content engine

A small, sustainable static-site generator. Content lives as plain files in
`content/`; `python build.py` renders the whole site (home + project pages),
plus `sitemap.xml`, `robots.txt`, JSON-LD, security headers (`_headers`), and
content-hashed CSS/JS. Output is written to the repo root and served by
Cloudflare. **Git is the database; Claude Code is the editor.**

## Edit content

- **A project** → `content/projects/<slug>/index.md` (TOML frontmatter + Markdown
  body) with hero/gallery images colocated in the same folder. Gallery images are
  declared via `[[gallery]]` (each `src` + `alt`).
- **Site-wide settings** → `content/settings.toml` (canonical domain, contact,
  SEO descriptions).
- **Home-page copy / layout** → `templates/home.html` (copy is inline; the project
  grid is generated from `content/projects/`).

Claude Code slash commands: `/add-project`, `/edit-project`, `/new-page`, `/publish`.

## Build & deploy

```
python build.py        # render everything to the repo root
python -m pytest -q     # engine unit tests
git add -A && git commit && git push origin main   # Cloudflare redeploys
```

The build is deterministic and validates content (missing fields, missing
images, duplicate slugs → it fails loudly).

## Layout

```
content/      the CMS (edit this)
templates/    Jinja2: home.html, project.html
static/       site.css sources -> build emits hashed copies; site.js (shared, CSP-safe)
engine/       parsers, validators, image/SEO/security/asset helpers
build.py      the engine entrypoint
tools/        one-time importer, parity harness, legacy scripts
docs/superpowers/  the design spec + plan
```

## Dependencies

`Jinja2` (templating) and `Pillow` (used by the `tools/` parity + crop scripts).
Everything else is Python stdlib. No JS toolchain, no framework. See `requirements.txt`.

## Set the canonical domain

`content/settings.toml` → `canonical_base`. Every canonical/OG/sitemap/robots/
JSON-LD URL derives from it. Set it to the real domain before going live.

## Deferred (safe follow-ups)

Not yet built — to be added (and parity-verified) when needed: responsive WebP
images (`<picture>`/`srcset`), self-hosted fonts (then tighten the CSP to drop the
Google Fonts origins), CSS/JS minification, and generic `content/pages/` rendering.
The earlier unused scaffolding for these was removed to keep the engine lean; see
the design intent in `docs/superpowers/specs/2026-06-14-content-engine-design.md`.
