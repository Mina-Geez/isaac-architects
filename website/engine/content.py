import dataclasses
import pathlib

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
    featured: bool
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
        featured=bool(meta.get("featured", False)),
        body_html=render_paragraphs(body), gallery=gallery, dir=folder)


def load_projects(projects_dir: pathlib.Path) -> list:
    items = [load_project(d) for d in sorted(projects_dir.iterdir()) if d.is_dir()]
    slugs = [p.slug for p in items]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise ContentError(f"duplicate slugs: {dupes}")
    return sorted([p for p in items if not p.draft], key=lambda p: p.order)
