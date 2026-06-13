"""Crop the workflow-picked PDF page renders to extract just the architectural visuals.

v2: bounds refined by the per-image review workflow."""
import os
from PIL import Image

SRC = r"C:\Users\test-\OneDrive\Desktop\Isaac Architects\pdf_pages"
DST = r"C:\Users\test-\OneDrive\Desktop\Isaac Architects\images"
os.makedirs(DST, exist_ok=True)

# (slug, source_filename, crop_top%, crop_bottom%, crop_left%, crop_right%)
PICKS = [
    ("vidorra-commercial-centre", "IDEA_ARCH_PROJECTS_(1)_p03.png",     20,  3, 46,  2),
    ("be-sagy-school",            "IDEA_ARCH_PROJECTS_(1)_p07.png",     28, 20,  4,  4),
    ("rakoty-school",             "IDEA_ARCH_PROJECTS_(1)_p11.png",      8,  4, 44,  5),
    ("panacea-2",                 "IDEA_ARCH_PROJECTS_(1)_p14.png",      0, 10,  0, 20),
    ("villa-tadros",              "IDEA_ARCH_PROJECTS_(1)_p17.png",     28,  2,  2,  2),
    ("villa-marc",                "IDEA_ARCH_PROJECTS_(1)_p19.png",     29, 22,  3,  3),
    ("villa-merry-land",          "IDEA_2025_p05.png",                  54,  3,  2,  2),
    ("afify-palace",              "IDEA_ARCH_PROJECTS_(1)_p22.png",     30, 15, 42,  3),
    ("sea-star-convention",       "IDEA_INTERIOR_PROJECTS_(2)_p19.png", 25,  8,  4, 14),
    ("royal-wedding-complex",     "IDEA_ARCH_PROJECTS_(1)_p30.png",     53,  3,  2, 54),
    ("saint-wanas-church",        "IDEA_ARCH_PROJECTS_(1)_p24.png",      0, 18,  0,  0),
    ("pope-kirilos-church",       "IDEA_ARCH_PROJECTS_(1)_p39.png",      2, 18,  1,  1),
    ("saint-cyril-medical",       "IDEA_2025_p10.png",                   3, 56,  2, 55),
    ("zafer-landscape",           "IDEA_2025_p12.png",                  17,  8, 10, 11),
    ("agora-bowling",             "IDEA_INTERIOR_PROJECTS_(2)_p03.png",  3,  1,  5,  3),
    ("charles-apartment",         "IDEA_INTERIOR_PROJECTS_(2)_p13.png", 52,  7, 58,  5),
    ("sandy-wedding-halls",       "IDEA_INTERIOR_PROJECTS_(2)_p23.png",  2,  2,  2, 50),
    ("archangel-rafaael",         "IDEA_INTERIOR_PROJECTS_(2)_p28.png",  8, 64,  6, 55),
]

MAX_WIDTH = 1600

for slug, fname, t, b, l, r in PICKS:
    src_path = os.path.join(SRC, fname)
    if not os.path.isfile(src_path):
        print(f"MISSING: {fname}")
        continue
    img = Image.open(src_path).convert("RGB")
    W, H = img.size
    left = int(W * l / 100)
    right = W - int(W * r / 100)
    top = int(H * t / 100)
    bottom = H - int(H * b / 100)
    cropped = img.crop((left, top, right, bottom))

    cw, ch = cropped.size
    if cw > MAX_WIDTH:
        new_h = int(ch * (MAX_WIDTH / cw))
        cropped = cropped.resize((MAX_WIDTH, new_h), Image.LANCZOS)

    out = os.path.join(DST, f"{slug}.jpg")
    cropped.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"{slug:30s} {cropped.size[0]:>4}x{cropped.size[1]:<4}  ({os.path.getsize(out)//1024} KB)")

print(f"\nDone. {len(PICKS)} images in {DST}")
