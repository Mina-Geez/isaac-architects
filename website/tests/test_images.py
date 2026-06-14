from PIL import Image
from engine.images import emit_variants, emit_fallback


def test_emits_jpg_webp_and_widths(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (2000, 1500), (120, 100, 80)).save(src, "JPEG")
    out = tmp_path / "out"
    out.mkdir()
    written = emit_variants(src, out, "villa", widths=(480, 960, 1400))
    names = {p.name for p in written}
    assert "villa-1400.jpg" in names
    assert "villa-480.webp" in names
    assert all("1999" not in n for n in names)


def test_fallback_caps_width(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (2000, 1000), (10, 20, 30)).save(src, "JPEG")
    out = tmp_path / "out"
    out.mkdir()
    p = emit_fallback(src, out, "villa", max_width=1400)
    assert p.name == "villa.jpg"
    assert Image.open(p).size[0] == 1400
