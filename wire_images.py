"""Replace gradient placeholder divs with real <img> tags in the website HTML."""
import re

HTML = r"C:\Users\test-\OneDrive\Desktop\Isaac Architects\isaac-architects-website.html"

# gradient class -> (slug, alt text)
MAP = {
    "grad-1":  ("vidorra-commercial-centre",  "Vidorra Commercial Centre — exterior rendering"),
    "grad-2":  ("be-sagy-school",              "BE Sagy International School Complex — rotunda rendering"),
    "grad-3":  ("rakoty-school",               "Rakoty Language National School — entrance"),
    "grad-4":  ("panacea-2",                   "Panacea 2 Compound — dusk view"),
    "grad-5":  ("villa-tadros",                "Villa Tadros — modern villa exterior"),
    "grad-6":  ("villa-marc",                  "Villa Marc — interior"),
    "grad-7":  ("villa-merry-land",            "Villa Merry Land — front entry"),
    "grad-8":  ("afify-palace",                "Afify Palace — palatial residence"),
    "grad-9":  ("sea-star-convention",         "Sea Star Convention Centre — banquet hall"),
    "grad-10": ("royal-wedding-complex",       "Royal Wedding Complex — exterior"),
    "grad-11": ("saint-wanas-church",          "Saint Wanas Church — exterior"),
    "grad-12": ("pope-kirilos-church",         "Pope Kirilos Church — dome and stained glass"),
    "grad-13": ("saint-cyril-medical",         "Saint Cyril Medical Center — exterior"),
    "grad-14": ("zafer-landscape",             "Zafer Property Landscape — site plan"),
    "grad-15": ("agora-bowling",               "Agora Bowling & Gaming Center — interior"),
    "grad-16": ("charles-apartment",           "Charles Apartment — kitchen"),
    "grad-17": ("sandy-wedding-halls",         "Sandy Wedding Halls — interior"),
    "grad-18": ("archangel-rafaael",           "Archangel Rafaael Nursing Home — hall"),
}

with open(HTML, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Ensure .project-img sizing works for <img> too
src = src.replace(
    ".project-img{position:absolute;inset:0;transition:transform .8s cubic-bezier(.4,0,.2,1)}",
    ".project-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;transition:transform .8s cubic-bezier(.4,0,.2,1)}"
)

# 2. Replace each `<div class="project-img grad-N"></div>` with an <img> in the project grid
for cls, (slug, alt) in MAP.items():
    pattern = re.compile(r'<div class="project-img ' + re.escape(cls) + r'"></div>')
    img_tag = f'<img class="project-img" src="images/{slug}.jpg" alt="{alt}" loading="lazy">'
    new, n = pattern.subn(img_tag, src)
    if n == 0:
        print(f"WARN: no match for {cls}")
    src = new

# 3. Featured section uses inline-styled grad-2 div — swap to BE Sagy image
src = src.replace(
    '<div class="project-img grad-2" style="position:absolute;inset:0"></div>',
    '<img class="project-img" src="images/be-sagy-school.jpg" alt="BE Sagy International School Complex" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">'
)

with open(HTML, "w", encoding="utf-8") as f:
    f.write(src)

print(f"Wired {len(MAP)} project images + featured image. File size: {len(src)//1024} KB")
