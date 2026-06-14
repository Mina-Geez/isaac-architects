import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent   # the website/ folder (served root)
WORKSPACE = ROOT.parent                                  # parent workspace (website + proposals + brand)
CONTENT = ROOT / "content"
PROJECTS = CONTENT / "projects"
SETTINGS = CONTENT / "settings.toml"
TEMPLATES = ROOT / "templates"
STATIC_SRC = ROOT / "static"
IMAGES_OUT = ROOT / "images"
STATIC_OUT = ROOT / "static"
BRAND_SRC = WORKSPACE / "brand"  # shared brand source of truth (logos master)
BRAND_OUT = ROOT / "brand"       # logos copied here so the site is self-contained + deployable
