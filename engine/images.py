import pathlib

from PIL import Image

WIDTHS = (480, 960, 1400)
QUALITY = 82


def emit_variants(src: pathlib.Path, out_dir: pathlib.Path, stem: str,
                  widths=WIDTHS, quality=QUALITY):
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


def emit_fallback(src: pathlib.Path, out_dir: pathlib.Path, stem: str,
                  max_width=1400, quality=QUALITY):
    """Write the legacy-named full-size fallback <stem>.jpg (URL-stable)."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    if w > max_width:
        img = img.resize((max_width, round(h * (max_width / w))), Image.LANCZOS)
    out = out_dir / f"{stem}.jpg"
    img.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return out
