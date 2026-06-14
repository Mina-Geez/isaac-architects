import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PROJECTS = CONTENT / "projects"
PAGES = CONTENT / "pages"
SETTINGS = CONTENT / "settings.toml"
TEMPLATES = ROOT / "templates"
STATIC_SRC = ROOT / "static"
OUT = ROOT                      # output is the repo root (deploy unchanged)
IMAGES_OUT = ROOT / "images"
STATIC_OUT = ROOT / "static"
