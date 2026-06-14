"""Isaac Architects content engine — render the whole site from content/.

Usage: python build.py
Reads content/ (settings + projects), renders Jinja templates, copies images,
emits hashed CSS/JS, sitemap.xml, robots.txt, _headers, security.txt.
Output is written to the repo root (deploy unchanged).
"""
import datetime
import re
import shutil
from urllib.parse import quote

from engine import paths
from engine.assets import hashed_name
from engine.content import load_projects
from engine.render import make_env, gallery_shapes
from engine.seo import (sitemap_xml, robots_txt, localbusiness_jsonld,
                        creativework_jsonld)
from engine.security import headers_file, security_txt
from engine.settings import load_settings

ROOT = paths.ROOT


def emit_static(src_name: str) -> str:
    """Hash + copy a static source file; return its hashed public name."""
    src = paths.STATIC_SRC / src_name
    raw = src.read_bytes()
    name = hashed_name(src_name, raw)
    paths.STATIC_OUT.mkdir(parents=True, exist_ok=True)
    (paths.STATIC_OUT / name).write_bytes(raw)
    return name


def copy_images(project):
    paths.IMAGES_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project.dir / project.hero, paths.IMAGES_OUT / f"{project.slug}.jpg")
    for i, item in enumerate(project.gallery, start=1):
        shutil.copy2(project.dir / item.src, paths.IMAGES_OUT / f"{project.slug}-{i}.jpg")


def prune_stale(keep_static, projects):
    """Remove build artifacts that no longer match current content, so repeated
    builds are idempotent and the served tree never accumulates orphans (old
    hashed CSS/JS, pages for deleted projects, images for removed galleries)."""
    removed = []
    # Stale hashed CSS/JS — keep only this build's freshly-emitted files. Match
    # only hashed output names (stem.<10hex>.ext); never the unhashed source
    # files (home.css, site.js, …) that live in the same static/ directory.
    hashed = re.compile(r".+\.[0-9a-f]{10}\.(css|js)$")
    if paths.STATIC_OUT.exists():
        for f in paths.STATIC_OUT.glob("*"):
            if f.is_file() and hashed.match(f.name) and f.name not in keep_static:
                f.unlink()
                removed.append(f"static/{f.name}")
    # Orphaned project pages.
    slugs = {p.slug for p in projects}
    proj_dir = ROOT / "projects"
    if proj_dir.exists():
        for f in proj_dir.glob("*.html"):
            if f.stem not in slugs:
                f.unlink()
                removed.append(f"projects/{f.name}")
    # Orphaned project images — keep og-image plus the current hero/gallery set.
    keep_images = {"og-image.jpg"}
    for p in projects:
        keep_images.add(f"{p.slug}.jpg")
        for i in range(1, len(p.gallery) + 1):
            keep_images.add(f"{p.slug}-{i}.jpg")
    if paths.IMAGES_OUT.exists():
        for f in paths.IMAGES_OUT.glob("*"):
            if (f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
                    and f.name not in keep_images):
                f.unlink()
                removed.append(f"images/{f.name}")
    return removed


def copy_brand():
    """Copy the served logo SVGs from the shared workspace brand/ into website/brand/
    so the deployed site is self-contained. brand/ stays the single source of truth."""
    logos = ["logo-mark.svg", "logo-lockup-dark.svg", "logo-lockup-light.svg"]
    paths.BRAND_OUT.mkdir(parents=True, exist_ok=True)
    for f in logos:
        src = paths.BRAND_SRC / f
        if src.exists():
            shutil.copy2(src, paths.BRAND_OUT / f)
        else:
            print(f"  ! brand asset missing: {src}")


def main():
    s = load_settings(paths.SETTINGS)
    base = s["canonical_base"]
    contact = s["contact"]
    projects = load_projects(paths.PROJECTS)
    env = make_env()
    lastmod = datetime.date.today().isoformat()

    copy_brand()
    css_home = emit_static("home.css")
    css_proj = emit_static("project.css")
    js = emit_static("site.js")

    # ---- project pages ----
    (ROOT / "projects").mkdir(exist_ok=True)
    n = len(projects)
    for i, p in enumerate(projects):
        copy_images(p)
        prev_p = projects[(i - 1) % n]
        next_p = projects[(i + 1) % n]
        wa_text = quote(f"Hi Isaac Architects, I'm interested in a project like {p.name}.")
        html = env.get_template("project.html").render(
            prefix="../",
            project=p, prev=prev_p, next=next_p,
            canonical=f"{base}/projects/{p.slug}",
            og_image=f"{base}/images/{p.slug}.jpg",
            contact=contact,
            wa_href=f"https://wa.me/{contact['whatsapp']}?text={wa_text}",
            shapes=gallery_shapes(len(p.gallery)),
            css_href=css_proj, js_href=js,
            jsonld=creativework_jsonld(base, p),
        )
        (ROOT / "projects" / f"{p.slug}.html").write_text(html, encoding="utf-8")

    # ---- home ----
    seo = s.get("seo", {})
    home_html = env.get_template("home.html").render(
        prefix="",
        projects=projects,
        canonical=f"{base}/",
        og_image=f"{base}/images/og-image.jpg",
        description=seo.get("description", ""),
        og_description=seo.get("og_description", ""),
        twitter_description=seo.get("twitter_description", ""),
        contact=contact,
        css_href=css_home, js_href=js,
        jsonld=localbusiness_jsonld(base, s["studio_name"],
                                    contact["phone_e164"], contact["location"],
                                    seo.get("description", "")),
    )
    (ROOT / "index.html").write_text(home_html, encoding="utf-8")

    # ---- 404 (Cloudflare serves /404.html for any not-found path) ----
    (ROOT / "404.html").write_text(
        env.get_template("404.html").render(), encoding="utf-8")

    # ---- SEO + security artifacts ----
    sitemap_paths = [""] + [f"projects/{p.slug}" for p in projects]
    (ROOT / "sitemap.xml").write_text(sitemap_xml(base, sitemap_paths, lastmod), encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots_txt(base), encoding="utf-8")
    (ROOT / "_headers").write_text(headers_file(), encoding="utf-8")
    wk = ROOT / ".well-known"
    wk.mkdir(exist_ok=True)
    (wk / "security.txt").write_text(security_txt(contact["email"]), encoding="utf-8")

    # ---- prune stale artifacts (idempotent build) ----
    removed = prune_stale({css_home, css_proj, js}, projects)
    if removed:
        print(f"  pruned {len(removed)} stale file(s): {', '.join(removed)}")

    print(f"Built home + {n} project pages.")
    print(f"  css: {css_home}, {css_proj} | js: {js}")
    print(f"  sitemap: {len(sitemap_paths)} urls | canonical_base: {base}")


if __name__ == "__main__":
    main()
