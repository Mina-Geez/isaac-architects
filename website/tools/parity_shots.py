"""Capture home + sample project pages at mobile+desktop for parity diffing.
Usage: python tools/parity_shots.py <out_dir>"""
import sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "projects/villa-tadros.html", "projects/saint-cyril-medical.html",
         "projects/be-sagy-school.html"]
VIEWPORTS = {
    "mobile": dict(viewport={"width": 430, "height": 932}, device_scale_factor=2,
                   is_mobile=True, has_touch=True),
    "desktop": dict(viewport={"width": 1366, "height": 900}),
}


def main(out_dir, root_dir=None):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    root = pathlib.Path(root_dir).resolve() if root_dir else ROOT
    base = root.as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            # reduced-motion -> the site's own CSS forces reveals/hero to final state,
            # removing animation-timing flicker so the diff measures layout, not timing.
            ctx = b.new_context(reduced_motion="reduce", **vp)
            for page in PAGES:
                pg = ctx.new_page(); pg.goto(f"{base}/{page}"); pg.wait_for_timeout(1200)
                name = page.replace("/", "_").replace(".html", "")
                pg.screenshot(path=str(out / f"{name}.{vp_name}.png"), full_page=True)
            ctx.close()
        b.close()
    print("wrote shots to", out, "from", root)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tools/_parity/before",
         sys.argv[2] if len(sys.argv) > 2 else None)
