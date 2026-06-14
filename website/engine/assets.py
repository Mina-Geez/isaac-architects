import hashlib
import pathlib
import shutil

import rcssmin
import rjsmin


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
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_bytes(out)
    return name


def copy_fonts(src_dir: pathlib.Path, out_dir: pathlib.Path):
    if not src_dir.exists():
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in src_dir.glob("*.woff2"):
        shutil.copy2(f, out_dir / f.name)
