"""Isaac Architects content engine — render the whole site from content/.

Usage: python build.py
Reads content/ (settings + projects), renders Jinja templates, copies images,
emits hashed CSS/JS, sitemap.xml, robots.txt, _headers, security.txt.
Output is written to the repo root (deploy unchanged).
"""
import datetime
import hashlib
import pathlib
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


def main():
    s = load_settings(paths.SETTINGS)
    base = s["canonical_base"]
    contact = s["contact"]
    projects = load_projects(paths.PROJECTS)
    env = make_env()
    lastmod = datetime.date.today().isoformat()

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
                                    contact["phone_e164"], contact["location"]),
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

    print(f"Built home + {n} project pages.")
    print(f"  css: {css_home}, {css_proj} | js: {js}")
    print(f"  sitemap: {len(sitemap_paths)} urls | canonical_base: {base}")


if __name__ == "__main__":
    main()
