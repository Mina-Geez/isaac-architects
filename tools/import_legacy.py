"""One-time: migrate the legacy PROJECTS dict + gallery_data.json into content/.

Reads the PROJECTS list literal out of generate_project_pages.py (without executing
its build), plus gallery_data.json, and writes content/projects/<slug>/index.md +
colocated hero/gallery images. Idempotent: overwrites content/projects/*.
"""
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_IMAGES = ROOT / "images"
OUT = ROOT / "content" / "projects"

MIN_QUALITY = 3
MAX_PER_PROJECT = 8

# Home-grid order (from index.html) — the canonical portfolio order; also drives prev/next.
HOME_ORDER = [
    "vidorra-commercial-centre", "be-sagy-school", "panacea-2", "villa-tadros",
    "sea-star-convention", "saint-wanas-church", "agora-bowling", "royal-wedding-complex",
    "villa-marc", "rakoty-school", "pope-kirilos-church", "sandy-wedding-halls",
    "villa-merry-land", "afify-palace", "saint-cyril-medical", "charles-apartment",
    "zafer-landscape", "archangel-rafaael",
]
FEATURED = {"vidorra-commercial-centre", "sea-star-convention", "sandy-wedding-halls"}


def extract_projects():
    text = (ROOT / "generate_project_pages.py").read_text(encoding="utf-8")
    start = text.index("PROJECTS = [")
    end = text.index("\n]", start) + 2
    ns = {}
    exec(text[start:end], ns)
    return ns["PROJECTS"]


def toml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    projects = {p["slug"]: p for p in extract_projects()}
    gallery_data = json.loads((ROOT / "gallery_data.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    for slug in HOME_ORDER:
        p = projects[slug]
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)

        # hero
        hero_src = SRC_IMAGES / f"{slug}.jpg"
        if hero_src.exists():
            shutil.copy2(hero_src, folder / "hero.jpg")
        else:
            print(f"  ! missing hero for {slug}")

        # gallery: same filter the legacy build used, mapped to existing images/<slug>-N.jpg
        visuals = [v for v in gallery_data.get(slug, []) if (v.get("quality") or 0) >= MIN_QUALITY]
        visuals = visuals[:MAX_PER_PROJECT]
        gallery_lines = []
        for i, v in enumerate(visuals, start=1):
            img = SRC_IMAGES / f"{slug}-{i}.jpg"
            if not img.exists():
                continue
            dst = folder / f"{i:02d}.jpg"
            shutil.copy2(img, dst)
            alt = v.get("description") or p["name"]
            gallery_lines.append(f"[[gallery]]\nsrc = {toml_str(dst.name)}\nalt = {toml_str(alt)}")

        fm = [
            f'name = {toml_str(p["name"])}',
            f'location = {toml_str(p["location"])}',
            f'category = {toml_str(p["category"])}',
            f'type = {toml_str(p["type"])}',
            f'area = {toml_str(p["area"])}',
            f'status = {toml_str(p["status"])}',
            f'lead = {toml_str(p["lead"])}',
            'hero = "hero.jpg"',
            f"order = {HOME_ORDER.index(slug) + 1}",
            f"featured = {'true' if slug in FEATURED else 'false'}",
            f"draft = false",
        ]
        body = "\n\n".join(p["body"])
        doc = "+++\n" + "\n".join(fm) + "\n" + "\n".join(gallery_lines) + "\n+++\n\n" + body + "\n"
        (folder / "index.md").write_text(doc, encoding="utf-8")
        print(f"  {slug:28s} {len(gallery_lines)} gallery images")

    print(f"Imported {len(HOME_ORDER)} projects into {OUT}")


if __name__ == "__main__":
    main()
