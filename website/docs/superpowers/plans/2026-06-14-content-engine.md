# Isaac Architects Content Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hardcoded `generate_project_pages.py` + hand-edited `index.html` with a sustainable, Claude-Code-operated content engine that renders the whole site from `content/` files, emits SEO + security + performance layers, and preserves the current design byte-for-byte.

**Architecture:** Content lives as TOML-frontmatter + Markdown files under `content/`. A single `build.py` loads + validates content, processes images (JPEG + WebP + responsive widths), renders Jinja2 templates, and emits `sitemap.xml`, `robots.txt`, JSON-LD, `_headers`, `security.txt`, and content-hashed CSS/JS. Output is written to the repo root; deploy (commit → push → Cloudflare) is unchanged.

**Tech Stack:** Python 3.12, Jinja2, Pillow, stdlib (`tomllib`, `hashlib`, `pathlib`, `html`, `xml.etree`, `urllib.parse`); pytest for tests; Playwright (already installed) for visual parity.

**Spec:** `docs/superpowers/specs/2026-06-14-content-engine-design.md`

---

## File Structure

```
build.py                     # CLI entrypoint: `python build.py`
engine/
  __init__.py
  frontmatter.py             # split +++ TOML +++ body; parse
  markdown.py                # tiny paragraph + emphasis renderer
  content.py                 # load/validate Project, Page, Settings models
  images.py                  # resize -> jpg/webp/responsive widths
  assets.py                  # minify + content-hash css/js, copy fonts
  seo.py                     # canonical/og head data, sitemap, robots, json-ld
  security.py                # _headers, security.txt
  render.py                  # Jinja2 environment + page rendering
  paths.py                   # central path constants (repo root, content, output)
templates/
  base.html  _head.html  _nav.html  _footer.html  _scripts.html
  home.html  project.html  page.html
  partials/_picture.html     # <picture> srcset macro
static/
  site.css                   # the EXACT current CSS, extracted once
  site.js                    # the EXACT current JS, extracted once
  fonts/                     # vendored woff2 (added in Phase 5)
content/
  settings.toml
  projects/<slug>/index.md (+ images)
tools/
  import_legacy.py           # one-time: PROJECTS dict + gallery_data.json -> content/
  fetch_fonts.py             # one-time: download Google woff2 -> static/fonts/
  crop_project_images.py     # MOVED here (legacy)
tests/
  test_frontmatter.py  test_markdown.py  test_content.py
  test_images.py  test_assets.py  test_seo.py  test_security.py
requirements.txt
README.md
.claude/commands/  add-project.md  edit-project.md  new-page.md  publish.md
```

**Output (committed, served by Cloudflare):** `index.html`, `projects/*.html`, `images/*.{jpg,webp}`, `static/site.<hash>.{css,js}`, `static/fonts/*`, `brand/*`, `sitemap.xml`, `robots.txt`, `_headers`, `.well-known/security.txt`.

---

## Phase 0 — Safety net & scaffolding

### Task 0.1: Branch + baseline parity screenshots

**Files:** Create: `tools/parity_shots.py`

- [ ] **Step 1: Create the branch**

Run:
```bash
git checkout -b content-engine
```

- [ ] **Step 2: Write the baseline screenshot script**

Create `tools/parity_shots.py`:
```python
"""Capture home + sample project pages at mobile+desktop for parity diffing.
Usage: python tools/parity_shots.py <out_dir>"""
import sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "projects/villa-tadros.html", "projects/saint-cyril-medical.html",
         "projects/be-sagy-school.html"]
VIEWPORTS = {"mobile": dict(width=430, height=932, device_scale_factor=2, is_mobile=True, has_touch=True),
             "desktop": dict(width=1366, height=900)}

def main(out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    base = ROOT.as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            ctx = b.new_context(reduced_motion="no-preference", **vp)
            for page in PAGES:
                pg = ctx.new_page(); pg.goto(f"{base}/{page}"); pg.wait_for_timeout(900)
                pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible'))")
                pg.wait_for_timeout(300)
                name = page.replace("/", "_").replace(".html", "")
                pg.screenshot(path=str(out / f"{name}.{vp_name}.png"), full_page=True)
            ctx.close()
        b.close()
    print("wrote baseline to", out)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tools/_parity/before")
```

- [ ] **Step 3: Capture the baseline (current site = source of truth)**

Run: `python tools/parity_shots.py tools/_parity/before`
Expected: PNGs written for 4 pages × 2 viewports = 8 files.

- [ ] **Step 4: Commit**
```bash
git add tools/parity_shots.py
git commit -m "test: baseline parity screenshot harness"
```
(The `tools/_parity/` images are gitignored — add `tools/_parity/` to `.gitignore` in this commit.)

### Task 0.2: Dependencies + test scaffolding

**Files:** Create: `requirements.txt`, `tests/__init__.py`, `engine/__init__.py`, `engine/paths.py`

- [ ] **Step 1: Write `requirements.txt`**
```
Jinja2>=3.1,<4
Pillow>=10,<12
pytest>=8,<9
rcssmin>=1.1,<2
rjsmin>=1.2,<2
```

- [ ] **Step 2: Install**

Run: `python -m pip install -r requirements.txt`
Expected: all install successfully.

- [ ] **Step 3: Write `engine/paths.py`**
```python
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC_SRC = ROOT / "static"
OUT = ROOT                      # output is the repo root (deploy unchanged)
IMAGES_OUT = ROOT / "images"
STATIC_OUT = ROOT / "static"
```

- [ ] **Step 4: Create empty `engine/__init__.py` and `tests/__init__.py`**

- [ ] **Step 5: Commit**
```bash
git add requirements.txt engine/ tests/
git commit -m "chore: engine scaffolding + deps"
```

---

## Phase 1 — Content core (TDD)

### Task 1.1: Frontmatter splitter/parser

**Files:** Create `engine/frontmatter.py`, `tests/test_frontmatter.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_frontmatter.py
import pytest
from engine.frontmatter import parse

def test_parses_toml_and_body():
    raw = '+++\nname = "Villa Tadros"\norder = 5\n+++\nFirst para.\n\nSecond para.'
    meta, body = parse(raw)
    assert meta["name"] == "Villa Tadros"
    assert meta["order"] == 5
    assert body.strip() == "First para.\n\nSecond para."

def test_missing_fences_raises():
    with pytest.raises(ValueError):
        parse("no fences here")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_frontmatter.py -v`
Expected: FAIL (`ModuleNotFoundError: engine.frontmatter`).

- [ ] **Step 3: Implement `engine/frontmatter.py`**
```python
import tomllib

FENCE = "+++"

def parse(raw: str):
    """Split a '+++ TOML +++ body' document into (dict, body_str)."""
    s = raw.lstrip("﻿").lstrip()
    if not s.startswith(FENCE):
        raise ValueError("missing opening +++ frontmatter fence")
    rest = s[len(FENCE):]
    end = rest.find("\n" + FENCE)
    if end == -1:
        raise ValueError("missing closing +++ frontmatter fence")
    toml_src = rest[:end]
    body = rest[end + len("\n" + FENCE):].lstrip("\n")
    meta = tomllib.loads(toml_src)
    return meta, body
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_frontmatter.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**
```bash
git add engine/frontmatter.py tests/test_frontmatter.py
git commit -m "feat(engine): toml frontmatter parser"
```

### Task 1.2: Markdown mini-renderer

**Files:** Create `engine/markdown.py`, `tests/test_markdown.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_markdown.py
from engine.markdown import render_paragraphs

def test_wraps_paragraphs():
    html = render_paragraphs("One.\n\nTwo.")
    assert html == "<p>One.</p>\n<p>Two.</p>"

def test_emphasis_and_escaping():
    html = render_paragraphs("a *b* & c")
    assert html == "<p>a <em>b</em> &amp; c</p>"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_markdown.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement `engine/markdown.py`**
```python
import re
from html import escape

_EM = re.compile(r"(?<!\w)[*_]([^*_]+)[*_](?!\w)")

def render_paragraphs(text: str) -> str:
    """Blank-line separated paragraphs; *word*/_word_ -> <em>. Escapes HTML."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    out = []
    for p in paras:
        safe = escape(p)
        safe = _EM.sub(r"<em>\1</em>", safe)
        out.append(f"<p>{safe}</p>")
    return "\n".join(out)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_markdown.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add engine/markdown.py tests/test_markdown.py
git commit -m "feat(engine): minimal markdown paragraph renderer"
```

### Task 1.3: Content models + validation

**Files:** Create `engine/content.py`, `tests/test_content.py`; test fixtures under `tests/fixtures/`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_content.py
import pytest, pathlib
from engine.content import load_project, ContentError

FIX = pathlib.Path(__file__).parent / "fixtures"

def test_loads_valid_project(tmp_path):
    d = tmp_path / "villa-x"; d.mkdir()
    (d / "01.jpg").write_bytes(b"x"); (d / "hero.jpg").write_bytes(b"x")
    (d / "index.md").write_text(
        '+++\nname="Villa X"\nlocation="Cairo"\ncategory="Residential"\n'
        'type="Villa"\nstatus="Built"\nlead="A lead."\nhero="hero.jpg"\norder=1\n'
        '[[gallery]]\nsrc="01.jpg"\nalt="A shot"\n+++\nBody para.', encoding="utf-8")
    p = load_project(d)
    assert p.slug == "villa-x"
    assert p.name == "Villa X"
    assert p.gallery[0].src == "01.jpg"
    assert "<p>Body para.</p>" in p.body_html

def test_missing_required_field_raises(tmp_path):
    d = tmp_path / "bad"; d.mkdir()
    (d / "index.md").write_text('+++\nname="No Lead"\n+++\nx', encoding="utf-8")
    with pytest.raises(ContentError):
        load_project(d)

def test_missing_gallery_image_raises(tmp_path):
    d = tmp_path / "g"; d.mkdir(); (d/"hero.jpg").write_bytes(b"x")
    (d / "index.md").write_text(
        '+++\nname="G"\nlocation="x"\ncategory="x"\ntype="x"\nstatus="x"\nlead="x"\nhero="hero.jpg"\norder=1\n'
        '[[gallery]]\nsrc="missing.jpg"\nalt="x"\n+++\nb', encoding="utf-8")
    with pytest.raises(ContentError):
        load_project(d)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_content.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement `engine/content.py`**
```python
import dataclasses, pathlib, tomllib
from engine.frontmatter import parse
from engine.markdown import render_paragraphs

REQUIRED = ("name", "location", "category", "type", "status", "lead")

class ContentError(Exception):
    pass

@dataclasses.dataclass
class GalleryItem:
    src: str
    alt: str

@dataclasses.dataclass
class Project:
    slug: str
    name: str
    location: str
    category: str
    type: str
    area: str
    status: str
    lead: str
    hero: str
    order: int
    draft: bool
    body_html: str
    gallery: list
    dir: pathlib.Path

def load_project(folder: pathlib.Path) -> Project:
    md = folder / "index.md"
    if not md.exists():
        raise ContentError(f"{folder}: missing index.md")
    meta, body = parse(md.read_text(encoding="utf-8"))
    for f in REQUIRED:
        if not meta.get(f):
            raise ContentError(f"{folder.name}: missing required field '{f}'")
    gallery = []
    for g in meta.get("gallery", []):
        if "src" not in g or "alt" not in g:
            raise ContentError(f"{folder.name}: gallery entry needs src+alt")
        if not (folder / g["src"]).exists():
            raise ContentError(f"{folder.name}: gallery image '{g['src']}' not found")
        gallery.append(GalleryItem(src=g["src"], alt=g["alt"]))
    hero = meta.get("hero", "hero.jpg")
    if not (folder / hero).exists():
        raise ContentError(f"{folder.name}: hero image '{hero}' not found")
    return Project(
        slug=folder.name, name=meta["name"], location=meta["location"],
        category=meta["category"], type=meta["type"], area=meta.get("area", "—"),
        status=meta["status"], lead=meta["lead"], hero=hero,
        order=int(meta.get("order", 999)), draft=bool(meta.get("draft", False)),
        body_html=render_paragraphs(body), gallery=gallery, dir=folder)

def load_projects(projects_dir: pathlib.Path) -> list:
    items = [load_project(d) for d in sorted(projects_dir.iterdir()) if d.is_dir()]
    slugs = [p.slug for p in items]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise ContentError(f"duplicate slugs: {dupes}")
    return sorted([p for p in items if not p.draft], key=lambda p: p.order)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_content.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**
```bash
git add engine/content.py tests/test_content.py
git commit -m "feat(engine): project content model + validation"
```

### Task 1.4: Settings loader

**Files:** Create `engine/settings.py`, append to `tests/test_content.py` (or `tests/test_settings.py`)

- [ ] **Step 1: Write the failing test** (`tests/test_settings.py`)
```python
from engine.settings import load_settings

def test_loads_settings(tmp_path):
    (tmp_path / "settings.toml").write_text(
        'canonical_base="https://x.com/"\nstudio_name="Isaac"\n'
        '[contact]\nphone_e164="+201274348575"\n', encoding="utf-8")
    s = load_settings(tmp_path / "settings.toml")
    assert s["canonical_base"] == "https://x.com"   # trailing slash trimmed
    assert s["contact"]["phone_e164"] == "+201274348575"
```

- [ ] **Step 2: Run to verify fail.** Run: `python -m pytest tests/test_settings.py -v` → FAIL.

- [ ] **Step 3: Implement `engine/settings.py`**
```python
import tomllib, pathlib

def load_settings(path: pathlib.Path) -> dict:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if "canonical_base" not in data:
        raise ValueError("settings.toml: canonical_base required")
    data["canonical_base"] = data["canonical_base"].rstrip("/")
    return data
```

- [ ] **Step 4: Run to verify pass.** → PASS.
- [ ] **Step 5: Commit.** `git add engine/settings.py tests/test_settings.py && git commit -m "feat(engine): settings loader"`

---

## Phase 2 — Image pipeline (TDD)

### Task 2.1: Image variants (jpg + webp + responsive widths)

**Files:** Create `engine/images.py`, `tests/test_images.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_images.py
import pathlib
from PIL import Image
from engine.images import emit_variants

def test_emits_jpg_webp_and_widths(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (2000, 1500), (120, 100, 80)).save(src, "JPEG")
    out = tmp_path / "out"; out.mkdir()
    written = emit_variants(src, out, "villa", widths=(480, 960, 1400))
    names = {p.name for p in written}
    # base jpg + webp at each width
    assert "villa-1400.jpg" in names
    assert "villa-480.webp" in names
    # capped at max width (no upscaling beyond source-limited 1400)
    assert all("1999" not in n for n in names)
```

- [ ] **Step 2: Run to verify fail.** → FAIL.

- [ ] **Step 3: Implement `engine/images.py`**
```python
import pathlib
from PIL import Image

def emit_variants(src: pathlib.Path, out_dir: pathlib.Path, stem: str,
                  widths=(480, 960, 1400), quality=82):
    """Write <stem>-<w>.jpg and <stem>-<w>.webp for each width <= source width.
    Returns the list of written paths."""
    img = Image.open(src).convert("RGB")
    sw, sh = img.size
    written = []
    targets = [w for w in widths if w <= sw] or [min(widths)]
    for w in targets:
        h = round(sh * (w / sw))
        resized = img.resize((w, h), Image.LANCZOS)
        jpg = out_dir / f"{stem}-{w}.jpg"
        webp = out_dir / f"{stem}-{w}.webp"
        resized.save(jpg, "JPEG", quality=quality, optimize=True, progressive=True)
        resized.save(webp, "WEBP", quality=quality, method=6)
        written += [jpg, webp]
    return written
```

- [ ] **Step 4: Run to verify pass.** → PASS.
- [ ] **Step 5: Commit.** `git add engine/images.py tests/test_images.py && git commit -m "feat(engine): responsive jpg+webp image variants"`

> NOTE on parity: the current site references `images/<slug>.jpg` (hero) and `images/<slug>-N.jpg` (gallery). To keep URLs stable, the build ALSO writes the legacy-named full-size `images/<slug>.jpg` / `images/<slug>-N.jpg` as the `<picture>` fallback `src`, and uses `<stem>-<w>.{webp,jpg}` only inside `srcset`. Implemented in Task 4.2 (render) where naming is wired to templates.

---

## Phase 3 — Templating (extract current markup, no visual change)

### Task 3.1: Extract CSS and JS to static files

**Files:** Create `static/site.css`, `static/site.js`; Modify `index.html` (temporarily, to prove extraction) — but the authoritative extraction target is the templates.

- [ ] **Step 1:** Copy the entire contents of the current `<style>…</style>` block from `index.html` into `static/site.css` (strip the `<style>` tags). Copy the entire `<script>…</script>` block (the bottom one) into `static/site.js` (strip `<script>` tags).

- [ ] **Step 2:** The project-page CSS/JS currently lives in `generate_project_pages.py` (`CSS` string + `MENU_SCRIPT`). Confirm `static/site.css` is a SUPERSET (home CSS already contains all shared rules; project-only rules — `.project-hero`, `.meta-strip`, `.narrative`, `.gallery-*`, `.cta-band`, `.proj-nav`, `.to-top`, etc. — must be appended). Append the project-only CSS rules from `generate_project_pages.py`'s `CSS` into `static/site.css`. Append the project-only JS (IntersectionObserver, menu, to-top) — note it's identical logic to `site.js`; keep ONE shared `site.js` used by all pages.

- [ ] **Step 3: Commit.** `git add static/site.css static/site.js && git commit -m "refactor: extract shared CSS/JS to static/"`

### Task 3.2: Jinja2 environment + base/partials

**Files:** Create `engine/render.py`, `templates/base.html`, `templates/_head.html`, `templates/_nav.html`, `templates/_footer.html`, `templates/_scripts.html`

- [ ] **Step 1: Write `engine/render.py`**
```python
import jinja2
from engine.paths import TEMPLATES

def make_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES)),
        autoescape=jinja2.select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True)
    return env
```

- [ ] **Step 2: Build `templates/base.html`** — the shared shell. Move the `<!DOCTYPE>…<head>…</head><body>…</body>` skeleton here, with blocks:
```html
<!DOCTYPE html>
<html lang="en">
{% include "_head.html" %}
<body>
{% include "_nav.html" %}
{% block content %}{% endblock %}
{% include "_footer.html" %}
{% include "_scripts.html" %}
</body>
</html>
```
`_head.html` holds the `<meta>`/title/`<link rel=preload>` fonts + hashed CSS + canonical/og/json-ld blocks (variables: `title`, `description`, `canonical`, `og_image`, `jsonld`, `css_href`). `_nav.html` and `_footer.html` hold the current nav + mobile menu + footer markup (parameterized by `nav_prefix` so project pages can link with `../`). `_scripts.html` references the hashed `site.js`.

- [ ] **Step 3: Commit.** `git add engine/render.py templates/ && git commit -m "feat(templates): base shell + partials"`

### Task 3.3: Home, project, page templates

**Files:** Create `templates/home.html`, `templates/project.html`, `templates/page.html`, `templates/partials/_picture.html`

- [ ] **Step 1: `templates/partials/_picture.html`** — a macro that renders the `<picture>` with WebP + jpg + srcset:
```html
{% macro picture(stem, alt, sizes, eager=false, cls="") -%}
<picture>
  <source type="image/webp" srcset="/images/{{stem}}-480.webp 480w, /images/{{stem}}-960.webp 960w, /images/{{stem}}-1400.webp 1400w" sizes="{{sizes}}">
  <img class="{{cls}}" src="/images/{{stem}}.jpg"
       srcset="/images/{{stem}}-480.jpg 480w, /images/{{stem}}-960.jpg 960w, /images/{{stem}}-1400.jpg 1400w" sizes="{{sizes}}"
       alt="{{alt}}" {% if eager %}fetchpriority="high" decoding="async"{% else %}loading="lazy" decoding="async"{% endif %}>
</picture>
{%- endmacro %}
```

- [ ] **Step 2: `templates/home.html`** — `{% extends "base.html" %}`, port the current home `<body>` sections (hero, stats, quote, work grid, about, approach, contact + enquiry form, to-top). Replace hardcoded copy with `settings.home.*` variables and loop the project grid over `projects` (re-using the wide/feature rhythm: `class="project-card{{' wide' if loop.index0 in feature_indices}}"`). Use the `picture()` macro for card images.

- [ ] **Step 3: `templates/project.html`** — port the current project-page `<body>` (hero, meta-strip, narrative, gallery, cta-band, proj-nav). Move `gallery_shapes()` into `engine/render.py` as a helper and pass `shapes` to the template; render the gallery with the `picture()` macro and the `g-*` classes. Wire the CTA band Call/WhatsApp + prev/next from `settings.contact` and the project list.

- [ ] **Step 4: `templates/page.html`** — minimal generic page (title + rendered body) for future types.

- [ ] **Step 5: Commit.** `git add templates/ && git commit -m "feat(templates): home, project, page, picture macro"`

---

## Phase 4 — SEO emitters (TDD)

### Task 4.1: sitemap, robots, JSON-LD, head data

**Files:** Create `engine/seo.py`, `tests/test_seo.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_seo.py
from engine.seo import sitemap_xml, robots_txt, localbusiness_jsonld

def test_sitemap_lists_pages():
    xml = sitemap_xml("https://x.com", ["", "projects/villa-x.html"], lastmod="2026-06-14")
    assert "<loc>https://x.com/</loc>" in xml
    assert "<loc>https://x.com/projects/villa-x.html</loc>" in xml

def test_robots_points_to_sitemap():
    assert "Sitemap: https://x.com/sitemap.xml" in robots_txt("https://x.com")

def test_localbusiness_has_name_and_phone():
    j = localbusiness_jsonld("https://x.com", "Isaac Architects", "+201274348575", "Alexandria, Egypt")
    assert '"@type": "ProfessionalService"' in j or '"@type":"ProfessionalService"' in j
    assert "+201274348575" in j
```

- [ ] **Step 2: Run to verify fail.** → FAIL.

- [ ] **Step 3: Implement `engine/seo.py`**
```python
import json
from xml.sax.saxutils import escape as xesc

def sitemap_xml(base: str, paths, lastmod: str) -> str:
    urls = []
    for p in paths:
        loc = f"{base}/{p}" if p else f"{base}/"
        urls.append(f"  <url><loc>{xesc(loc)}</loc><lastmod>{lastmod}</lastmod></url>")
    body = "\n".join(urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")

def robots_txt(base: str) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"

def localbusiness_jsonld(base, name, phone, location) -> str:
    data = {"@context": "https://schema.org", "@type": "ProfessionalService",
            "name": name, "url": base + "/", "telephone": phone,
            "image": f"{base}/images/og-image.jpg",
            "address": {"@type": "PostalAddress", "addressLocality": "Alexandria",
                        "addressCountry": "EG"},
            "areaServed": "EG", "description": location}
    return json.dumps(data, ensure_ascii=False)

def creativework_jsonld(base, project) -> str:
    data = {"@context": "https://schema.org", "@type": "CreativeWork",
            "name": project.name, "image": f"{base}/images/{project.slug}.jpg",
            "description": project.lead, "locationCreated": project.location,
            "url": f"{base}/projects/{project.slug}.html"}
    return json.dumps(data, ensure_ascii=False)
```

- [ ] **Step 4: Run to verify pass.** → PASS.
- [ ] **Step 5: Commit.** `git add engine/seo.py tests/test_seo.py && git commit -m "feat(engine): sitemap, robots, json-ld"`

---

## Phase 5 — Security + performance layers (TDD)

### Task 5.1: `_headers` + security.txt

**Files:** Create `engine/security.py`, `tests/test_security.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_security.py
from engine.security import headers_file, security_txt

def test_headers_contains_csp_and_hsts():
    h = headers_file()
    assert "Content-Security-Policy:" in h
    assert "script-src 'self'" in h
    assert "Strict-Transport-Security:" in h
    assert "X-Content-Type-Options: nosniff" in h
    assert "Cache-Control: public, max-age=31536000, immutable" in h

def test_security_txt_has_contact():
    assert "Contact:" in security_txt("ideadesigns.arch@gmail.com")
```

- [ ] **Step 2: Run to verify fail.** → FAIL.

- [ ] **Step 3: Implement `engine/security.py`**
```python
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
       "script-src 'self'; font-src 'self'; connect-src 'self'; form-action 'self'; "
       "frame-ancestors 'none'; base-uri 'self'; upgrade-insecure-requests")

def headers_file() -> str:
    return (
        "/*\n"
        f"  Content-Security-Policy: {CSP}\n"
        "  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload\n"
        "  X-Content-Type-Options: nosniff\n"
        "  X-Frame-Options: DENY\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: geolocation=(), microphone=(), camera=(), browsing-topics=()\n"
        "\n"
        "/static/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/images/*\n  Cache-Control: public, max-age=31536000, immutable\n")

def security_txt(email: str) -> str:
    return f"Contact: mailto:{email}\nPreferred-Languages: en\n"
```

- [ ] **Step 4: Run to verify pass.** → PASS.
- [ ] **Step 5: Commit.** `git add engine/security.py tests/test_security.py && git commit -m "feat(engine): _headers + security.txt"`

### Task 5.2: Asset hashing + minification + font vendoring

**Files:** Create `engine/assets.py`, `tests/test_assets.py`, `tools/fetch_fonts.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_assets.py
from engine.assets import hashed_name, minify_css

def test_hashed_name_stable():
    assert hashed_name("site.css", b"a{b:1}") == hashed_name("site.css", b"a{b:1}")
    assert hashed_name("site.css", b"x") != hashed_name("site.css", b"y")

def test_minify_css_strips_comments_ws():
    out = minify_css("a {  color : red ; } /* c */")
    assert "/*" not in out and out.count(" ") < 4
```

- [ ] **Step 2: Run to verify fail.** → FAIL.

- [ ] **Step 3: Implement `engine/assets.py`**
```python
import hashlib, pathlib, shutil
import rcssmin, rjsmin

def hashed_name(name: str, content: bytes) -> str:
    h = hashlib.sha256(content).hexdigest()[:10]
    stem, _, ext = name.rpartition(".")
    return f"{stem}.{h}.{ext}"

def minify_css(css: str) -> str:
    return rcssmin.cssmin(css)

def minify_js(js: str) -> str:
    return rjsmin.jsmin(js)

def emit_hashed(src: pathlib.Path, out_dir: pathlib.Path, minifier) -> str:
    raw = src.read_text(encoding="utf-8")
    out = minifier(raw).encode("utf-8")
    name = hashed_name(src.name, out)
    (out_dir / name).write_bytes(out)
    return name

def copy_fonts(src_dir: pathlib.Path, out_dir: pathlib.Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in src_dir.glob("*.woff2"):
        shutil.copy2(f, out_dir / f.name)
```

- [ ] **Step 4: Run to verify pass.** → PASS.

- [ ] **Step 5: Write `tools/fetch_fonts.py`** (one-time, run manually) — download the exact woff2 files for Cormorant Garamond (300,400,500 + italic 400) and DM Sans (300,400,500) from the Google Fonts CSS API (set a desktop UA to get woff2 URLs), save into `static/fonts/`, and print a `@font-face` block to paste into `static/site.css`. Run it once: `python tools/fetch_fonts.py`. Commit the woff2 files.

- [ ] **Step 6: Commit.** `git add engine/assets.py tests/test_assets.py tools/fetch_fonts.py static/fonts/ static/site.css && git commit -m "feat(engine): asset hashing, minify, self-hosted fonts"`

> When fonts are self-hosted, REMOVE the `fonts.googleapis.com`/`gstatic.com` `<link>`s from `_head.html`, add `<link rel=preload as=font type=font/woff2 crossorigin>` for the two body weights, and replace the Google `@import`/`<link>` with the local `@font-face` block in `static/site.css`. This is required for the strict CSP to hold (no third-party origins).

---

## Phase 6 — Migration (port existing content, no design change)

### Task 6.1: Legacy importer

**Files:** Create `tools/import_legacy.py`

- [ ] **Step 1: Write `tools/import_legacy.py`** — read the `PROJECTS` list from the existing `generate_project_pages.py` (import it as a module or copy the list) and `gallery_data.json`; for each project create `content/projects/<slug>/index.md` with TOML frontmatter (name, location, category, type, area, status, lead, hero="hero.jpg", order=index, gallery entries from the cropped image list with their `description` as `alt`), and the `body` paragraphs as the Markdown body. Copy `images/<slug>.jpg` → `content/projects/<slug>/hero.jpg` and `images/<slug>-N.jpg` → `content/projects/<slug>/NN.jpg`.

- [ ] **Step 2: Run it.** Run: `python tools/import_legacy.py`
Expected: `content/projects/<slug>/` created for all 18 projects with `index.md` + images.

- [ ] **Step 3: Spot-check** one `index.md` (e.g. `content/projects/villa-tadros/index.md`) reads correctly.

- [ ] **Step 4: Commit.** `git add tools/import_legacy.py content/projects/ && git commit -m "chore: import 18 projects into content/"`

### Task 6.2: Port home copy + settings

**Files:** Create `content/settings.toml`

- [ ] **Step 1:** Transcribe into `content/settings.toml`: `canonical_base` (placeholder `https://isaac-architects.pages.dev` until the custom domain arrives), studio name, `[contact]` (phone_display, phone_e164, whatsapp, email, location), `[stats]` (the three stat items), and `[home]` (hero eyebrow/title_plain/title_accent/sub, the founder quote + attribution, about heading + body paragraphs, the three approach cards, contact heading + paragraph). Copy the EXACT current strings.

- [ ] **Step 2: Commit.** `git add content/settings.toml && git commit -m "chore: site settings + home copy as content"`

### Task 6.3: Wire `build.py`

**Files:** Create `build.py`

- [ ] **Step 1: Write `build.py`** — orchestrate: load settings; load projects; for each project + hero emit image variants AND legacy-named full-size fallback into `images/`; compute `gallery_shapes`; emit hashed `site.<hash>.css/js`; copy fonts; render `index.html`, `projects/*.html` (with canonical/og/json-ld from settings + seo helpers); write `sitemap.xml`, `robots.txt`, `_headers`, `.well-known/security.txt`. Print a summary. Keep functions small; the heavy lifting is already in `engine/*`.

- [ ] **Step 2: Run the build.** Run: `python build.py`
Expected: `index.html`, `projects/*.html`, images, static assets, sitemap, robots, `_headers`, security.txt all written; exit 0.

- [ ] **Step 3: Run all unit tests.** Run: `python -m pytest -q` → all pass.

- [ ] **Step 4: Commit.** `git add build.py index.html projects/ images/ static/ sitemap.xml robots.txt _headers .well-known/ && git commit -m "feat: build.py renders full site from content"`

---

## Phase 7 — Parity verification & cutover

### Task 7.1: Visual parity gate

- [ ] **Step 1: Capture the AFTER screenshots.** Run: `python tools/parity_shots.py tools/_parity/after`

- [ ] **Step 2: Write `tools/parity_diff.py`** — for each filename present in both `before/` and `after/`, compute a pixel difference ratio (Pillow `ImageChops.difference` → sum/maxsum); print any file with >0.5% differing pixels.
```python
import pathlib, sys
from PIL import Image, ImageChops
b = pathlib.Path("tools/_parity/before"); a = pathlib.Path("tools/_parity/after")
fail = False
for f in sorted(b.glob("*.png")):
    other = a / f.name
    if not other.exists(): print("MISSING after:", f.name); fail=True; continue
    i1, i2 = Image.open(f).convert("RGB"), Image.open(other).convert("RGB")
    if i1.size != i2.size:
        print(f"SIZE DIFF {f.name}: {i1.size} vs {i2.size}"); fail=True; continue
    diff = ImageChops.difference(i1, i2)
    ratio = sum(diff.getdata(0)) / (i1.size[0]*i1.size[1]*255)
    if ratio > 0.005: print(f"DIFF {f.name}: {ratio:.4%}"); fail=True
print("PARITY", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
```

- [ ] **Step 3: Run the diff.** Run: `python tools/parity_diff.py`
Expected: `PARITY PASS`. If any page differs, fix the template/CSS until it matches (common causes: whitespace in inlined SVG, font rendering before self-host — re-baseline AFTER fonts are self-hosted on BOTH sides by rebuilding the old output is not possible, so for font-affected diffs, verify by eye that only anti-aliasing differs).

- [ ] **Step 4: Commit.** `git add tools/parity_diff.py && git commit -m "test: visual parity gate (before vs after)"`

### Task 7.2: Retire the old generator + docs

**Files:** Delete `generate_project_pages.py`; Move `crop_project_images.py` → `tools/`; Modify `CLAUDE.md`; Create `README.md`

- [ ] **Step 1:** `git mv crop_project_images.py tools/crop_project_images.py`
- [ ] **Step 2:** `git rm generate_project_pages.py gallery_data.json` (content now lives in `content/`; keep a copy of `gallery_data.json` under `tools/_legacy/` if cautious).
- [ ] **Step 3:** Rewrite `CLAUDE.md` "Files"/"Build flow" sections to describe the engine (`content/` + `build.py`), and add `README.md` documenting: the content model, how to add a project/page, the slash commands, and the deploy (`python build.py` → commit → push).
- [ ] **Step 4: Commit.** `git add -A && git commit -m "docs: retire legacy generator, document content engine"`

---

## Phase 8 — Claude Code commands

### Task 8.1: Slash commands

**Files:** Create `.claude/commands/add-project.md`, `edit-project.md`, `new-page.md`, `publish.md`

- [ ] **Step 1: `add-project.md`** — instructions for Claude: ask for the fields, create `content/projects/<slug>/index.md`, prompt the user to drop hero/gallery images into the folder (or accept paths and copy them), run `python build.py`, run the parity shots for the new page, and show a preview. Include the exact frontmatter template.
- [ ] **Step 2: `edit-project.md`** — open `content/projects/<slug>/index.md`, apply requested edits, `python build.py`.
- [ ] **Step 3: `new-page.md`** — scaffold `content/pages/<slug>.md`; if a new type, create `templates/<type>.html`; build.
- [ ] **Step 4: `publish.md`** — `python build.py` then commit all output + content and `git push` using the one-shot author override from CLAUDE.md.
- [ ] **Step 5: Commit.** `git add .claude/commands/ && git commit -m "feat: Claude Code CMS slash commands"`

### Task 8.2: Merge

- [ ] **Step 1:** Open a PR `content-engine` → `main`, or fast-forward merge after a final `python build.py` + `python -m pytest -q` + `python tools/parity_diff.py` all green.
- [ ] **Step 2:** Push `main`; Cloudflare serves the rebuilt site. Verify the live `_headers` are applied (DevTools → Network → response headers show CSP/HSTS).

---

## Self-Review

**Spec coverage:** content model (Ph1,6) ✓; build engine (Ph1–6) ✓; SEO sitemap/robots/json-ld/canonical (Ph4, Task6.3) ✓; security layer `_headers`/CSP/externalized JS/self-host fonts (Ph5) ✓; performance WebP/srcset/hashed/cached/fonts (Ph2,5, picture macro) ✓; file reorg (Ph0,3,7) ✓; migration + parity gate (Ph6,7) ✓; Claude commands (Ph8) ✓; sustainability (pinned deps, validation, deterministic, quarantined tools, README) ✓.

**Placeholder scan:** `canonical_base` uses an explicit placeholder domain (intended — user supplies real domain); `fetch_fonts.py` and `import_legacy.py` are described procedurally because they parse existing repo data (the exact source — `PROJECTS` dict, `gallery_data.json`, current `<style>`/`<script>`) lives in the repo and must be transcribed verbatim, not invented. All engine logic tasks contain complete code.

**Type consistency:** `Project`/`GalleryItem` fields used consistently across `content.py`, `seo.py` (`project.slug/name/lead/location`), templates, and `creativework_jsonld`. `emit_variants(stem)` naming matches the `picture()` macro's `<stem>-<w>.{webp,jpg}` and the legacy `<stem>.jpg` fallback. `hashed_name`/`emit_hashed` consistent.

**Known parity caveat (explicit, not a gap):** self-hosting fonts changes the font *delivery* not the font, but sub-pixel anti-aliasing may differ slightly from the Google-CDN-served version; the parity gate's 0.5% threshold absorbs anti-aliasing noise, and any flagged text-only diff is eyeballed.
