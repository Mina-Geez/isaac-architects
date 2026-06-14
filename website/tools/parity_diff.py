"""Compare tools/_parity/before vs after; report pages exceeding a pixel-diff threshold."""
import pathlib
import sys
from PIL import Image, ImageChops

b = pathlib.Path("tools/_parity/before")
a = pathlib.Path("tools/_parity/after")
THRESH = 0.005
fail = False
for f in sorted(b.glob("*.png")):
    other = a / f.name
    if not other.exists():
        print("MISSING after:", f.name); fail = True; continue
    i1, i2 = Image.open(f).convert("RGB"), Image.open(other).convert("RGB")
    if i1.size != i2.size:
        print(f"SIZE DIFF {f.name}: {i1.size} vs {i2.size}"); fail = True; continue
    diff = ImageChops.difference(i1, i2)
    ratio = sum(diff.getdata(0)) / (i1.size[0] * i1.size[1] * 255)
    flag = "  <-- DIFF" if ratio > THRESH else ""
    if ratio > THRESH:
        fail = True
    print(f"{f.name:45s} {ratio:.4%}{flag}")
print("PARITY", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
