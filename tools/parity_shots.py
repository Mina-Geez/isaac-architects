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


def main(out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    base = ROOT.as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            ctx = b.new_context(reduced_motion="no-preference", **vp)
            for page in PAGES:
                pg = ctx.new_page(); pg.goto(f"{base}/{page}"); pg.wait_for_timeout(1000)
                pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible'))")
                pg.wait_for_timeout(300)
                name = page.replace("/", "_").replace(".html", "")
                pg.screenshot(path=str(out / f"{name}.{vp_name}.png"), full_page=True)
            ctx.close()
        b.close()
    print("wrote baseline to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tools/_parity/before")
