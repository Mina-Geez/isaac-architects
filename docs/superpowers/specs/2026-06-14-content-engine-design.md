# Isaac Architects — Content Engine (Claude-Code-operated CMS)

**Date:** 2026-06-14
**Status:** Design — approved, pending spec review
**Author:** Claude (with Mina-Geez)

## 1. Summary

Replace the current hand-maintained build (`generate_project_pages.py` with a hardcoded
`PROJECTS` dict + the artisanal `index.html`) with a small, sustainable **content engine**:
content lives as plain files under `content/`, a single `build.py` renders the whole site
(home, projects, future page types) through Jinja2 templates, and Claude Code is the editing
interface via slash commands. Git is the database and the version history.

The same build also emits the SEO artifacts the site currently lacks (`sitemap.xml`,
`robots.txt`, JSON-LD structured data) and fixes the canonical-domain problem by deriving every
canonical/OG/sitemap URL from one `canonical_base` setting.

**Primary goals:** content/code separation, extensibility (new page types), sustainability
(minimal moving parts), and correct SEO. **Deploy is unchanged** — build locally, commit the
HTML, push, Cloudflare serves it.

## 2. Goals & non-goals

### Goals
- Edit all content (projects, home-page copy, contact, stats, future pages) as files, not code.
- Add a new project or change a phone number via Claude Code, then `/publish`.
- Support new content types later (journal, team) by adding a template + content folder.
- Generate `sitemap.xml`, `robots.txt`, and JSON-LD on every build.
- Single source of truth for the canonical domain.
- Preserve the existing visual design **exactly** (byte-for-byte parity at migration).

### Non-goals (YAGNI)
- No web admin UI, login, or backend (decided: "just me, via Claude Code").
- No headless CMS service or database.
- No Node/SSG framework (decided: low maintenance → Python).
- No deploy-pipeline change (no Cloudflare build step; output stays committed at repo root).
- No blog/journal content yet — only the *capability* (generic page type) is built now.

## 3. Sustainability principles (the "make it sustainable" mandate)

1. **Minimal, stable dependencies.** Runtime libs: `Jinja2` (templating) + `Pillow` (images,
   already used). Everything else is Python stdlib (`tomllib` for TOML, `pathlib`, `html`,
   `xml`). No npm, no framework, no transitive churn. Pin major versions in `requirements.txt`.
2. **Single source of truth.** `content/settings.toml` holds `canonical_base`, contact details,
   stats, and global copy. Every derived value (canonical, OG, sitemap, robots, JSON-LD) reads
   from it. Changing the domain is one edit.
3. **Deterministic & idempotent build.** Re-running `build.py` with unchanged content produces
   byte-identical output (stable ordering, no timestamps except content-declared `updated`).
4. **Validated content.** The build fails loudly on malformed frontmatter, missing required
   fields, missing images, or duplicate slugs — never silently produces a broken page.
5. **DRY templates.** Shared `head`, `nav`, `footer` partials; one template per content type.
6. **Quarantined legacy.** One-off import/crop scripts live in `tools/`, out of the build path.
7. **No lock-in.** Output is plain static HTML/CSS; content is plain Markdown+TOML. The engine
   can be replaced without touching content.
8. **Documented.** A `README.md` explains the model, the commands, and how to add a page type.
9. **Accessibility preserved.** Reduced-motion, focus states, alt text, and touch targets from
   the current site carry into the templates.

## 4. Content model

`content/` is the only directory authors touch.

```
content/
  settings.toml                     # global config + home-page copy
  projects/
    <slug>/
      index.md                      # TOML frontmatter + Markdown body
      hero.jpg                      # hero image (or declared in frontmatter)
      01.jpg, 02.jpg, ...           # gallery images (colocated)
  pages/
    <slug>.md                       # generic page (future: journal, team, ...)
```

### 4.1 `settings.toml`
```toml
canonical_base = "https://example.com"   # the one domain; drives all URLs
studio_name    = "Isaac Architects"
[contact]
phone_display = "+20 127 434 8575"
phone_e164    = "+201274348575"
whatsapp      = "201274348575"
email         = "ideadesigns.arch@gmail.com"
location      = "Alexandria, Egypt"
[stats]
items = [ {value="18+", label="Completed Projects"}, ... ]
[home]
hero_eyebrow = "Architecture · Interiors · Landscape"
hero_title_plain = "Shaping"
hero_title_accent = "spaces that endure"
hero_sub = "An architecture studio in Alexandria, composing light, stone, and proportion into spaces that grow truer with age."
# ...quote, about, approach cards, contact copy...
```

### 4.2 Project `index.md`
```
+++
name = "Villa Tadros"
location = "King Mariout, Egypt"
category = "Residential"
type = "Private Villa"
area = "650 sqm"
status = "Built"
lead = "A 650 square-meter modern minimalist villa — where the rendering became the building."
hero = "hero.jpg"
order = 5
draft = false
# optional per-image captions; otherwise alt falls back to project name
[[gallery]]
src = "01.jpg"
alt = "Villa Tadros — modern villa exterior"
+++

Generous horizontal massing, a restrained palette of stone and glass, and carefully
composed indoor-outdoor thresholds.

The completed work matches the original drawings with a fidelity that is its own kind of craft.
```
- Frontmatter format: **TOML** between `+++` fences (parsed by stdlib `tomllib`), chosen over
  YAML to avoid a dependency.
- Body: Markdown paragraphs (blank-line separated). A small built-in renderer handles paragraphs
  and `*emphasis*`/`_italics_` → `<em>`; no Markdown library needed for this prose.
- Required fields validated: `name, location, category, type, status, lead`. `area` defaults
  to "—". `order` controls grid/sort position. `draft = true` excludes from build + sitemap.
- **Gallery images are declared** explicitly via `[[gallery]]` entries (each `src` + `alt`),
  not auto-discovered — this keeps order deterministic and guarantees real alt text (SEO/a11y).
  The build validates every declared `src` exists; a stray image file with no entry is ignored.
  The editorial mosaic order (`gallery_shapes()`) is derived from the entry sequence.

### 4.3 Generic page `pages/<slug>.md`
Same `+++` TOML + Markdown body, with `template = "page"` (or another type) and `title`,
`description`. Adding a genuinely new *type* = add `templates/<type>.html` and set `template`.

## 5. Build engine — `build.py`

Pipeline (pure functions, each independently testable):

1. **Load** `settings.toml`; validate.
2. **Discover & parse** all `content/projects/*/index.md` and `content/pages/*.md`; validate;
   sort by `order`. Fail on duplicate slug or missing required field/image.
3. **Process images**: for each project, copy/resize from the project folder to the public
   `images/` path, preserving today's URL scheme so no links change — hero → `images/<slug>.jpg`,
   gallery → `images/<slug>-N.jpg` (Pillow; same quality/max-width 1400 as today).
4. **Render** via Jinja2:
   - `home.html` ← settings + project list (the grid, with the existing 2-col/feature rhythm).
   - `project.html` ← each project (hero, meta, narrative, editorial gallery mosaic, CTA band,
     prev/next). The gallery `gallery_shapes()` logic and the CTA band move into the template/helpers.
   - `page.html` ← each generic page.
5. **SEO emit**: `sitemap.xml`, `robots.txt`, and inject per-page `<head>` (canonical, OG,
   Twitter, JSON-LD) — all from `canonical_base`.
6. **Write** output to repo root (`index.html`, `projects/*.html`, `images/*`, `sitemap.xml`,
   `robots.txt`). `brand/` is static, untouched.

Templates live in `templates/` with partials `_head.html`, `_nav.html`, `_footer.html`,
`_scripts.html`. The current CSS is preserved verbatim in `static/site.css` and linked (or
inlined via a partial to keep the single-file feel — decided at implementation, parity is the test).

## 6. SEO specifics

- **Canonical/OG/Twitter** per page from `canonical_base` + path. Fixes the github.io mismatch.
- **`sitemap.xml`**: home + every non-draft project + every page, with `<lastmod>` from each
  file's content-declared `updated` (or git mtime fallback).
- **`robots.txt`**: `User-agent: *` `Allow: /` + `Sitemap: <canonical_base>/sitemap.xml`.
- **JSON-LD**:
  - Home: `LocalBusiness`/`ProfessionalService` — name, Alexandria address, phone, `url`, logo,
    `sameAs` (socials when provided).
  - Project: `CreativeWork` — name, `image` (hero, absolute URL), description (lead), `locationCreated`.
- Per-page unique `<title>` + meta description from content (no change in voice).

## 7. File organization (final)

```
content/            # CMS — the only thing you edit
templates/          # Jinja2 templates + partials
static/             # site.css (preserved), any static assets
build.py            # the engine
requirements.txt    # jinja2, pillow (pinned majors)
README.md           # how the engine + commands work
tools/              # crop_project_images.py, one-time importer (off the build path)
docs/superpowers/specs/   # this spec
.claude/commands/   # /add-project, /edit-project, /new-page, /publish
# committed build output, served by Cloudflare (unchanged deploy):
index.html  projects/*.html  images/*  brand/*  sitemap.xml  robots.txt
```

## 8. Claude Code interface (the "CMS")

Custom slash commands in `.claude/commands/`:
- **`/add-project`** — gather fields, create `content/projects/<slug>/index.md`, guide image
  placement, run build, show a preview.
- **`/edit-project <slug>`** — open the content file, apply edits, rebuild.
- **`/new-page`** — scaffold `content/pages/<slug>.md` (and a template if a new type).
- **`/publish`** — build, then commit + push (the deploy action; one-shot git author override
  per CLAUDE.md).

Ad-hoc edits ("change the WhatsApp number", "mark Villa Marc as Built") are just natural-language
requests; Claude edits the content file and rebuilds. No command required.

## 9. Migration plan (one-time, on a branch)

1. Scaffold `content/`, `templates/`, `static/`, `build.py` alongside the current site.
2. **Importer** (`tools/import_legacy.py`): generate `content/projects/<slug>/index.md` from the
   existing `PROJECTS` dict + `gallery_data.json`; move existing `images/<slug>*.jpg` into each
   project folder as `hero.jpg`/`NN.jpg`.
3. Port `index.html` copy into `settings.toml` + `templates/home.html`; port the project page
   markup into `templates/project.html`. Preserve CSS exactly.
4. Run `build.py`; **verify byte-for-byte / visual parity** against the current output with
   Playwright screenshots (home + several projects, mobile + desktop) before merging.
5. Wire SEO; set `canonical_base` to the custom domain (placeholder until provided).
6. Retire `generate_project_pages.py` (its logic now lives in the engine); keep
   `crop_project_images.py` in `tools/`.

## 10. Dependencies

`requirements.txt`: `Jinja2` (pinned to a major), `Pillow` (already used). Stdlib: `tomllib`,
`pathlib`, `html`, `xml.etree`, `urllib.parse`. No JS toolchain.

## 11. Testing & verification

- **Content validation** is part of the build (unit-testable pure validators).
- **Visual parity**: Playwright screenshot diff of home + sample projects (mobile + desktop)
  pre/post migration; must match.
- **Smoke**: assert `sitemap.xml` lists all non-draft pages; canonical URLs use `canonical_base`;
  no broken image refs; build is idempotent (run twice → no diff).

## 12. Open items

- **Custom domain string** (user to provide) → `canonical_base`. Placeholder until then; site
  keeps building and deploying.
- Inline CSS vs linked `static/site.css` — decided at implementation by whichever preserves parity
  most cleanly; both are sustainable.

## 13. Risks

- **Migration regressions** — mitigated by visual parity gate before merge.
- **Scope** — this is a real migration; executed on a branch, phased (engine → import → SEO →
  commands), each phase verified. Not shipped until parity passes.
