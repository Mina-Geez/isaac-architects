"""Generate one HTML page per project under projects/<slug>.html.

Loads gallery_data.json, crops every visual >= quality 3 to images/<slug>-N.jpg,
then renders the project pages with the full gallery.
Re-run any time — overwrites all images and all 18 project pages."""
import json
import os
from html import escape
from urllib.parse import quote
from PIL import Image

PHONE = "+201274348575"          # primary line (tel:)
WHATSAPP = "201274348575"        # same number, wa.me international format
PHONE_DISPLAY = "+20 127 434 8575"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "projects")
IMG_DIR = os.path.join(ROOT, "images")
PAGES_DIR = os.path.join(ROOT, "pdf_pages")
GALLERY_JSON = os.path.join(ROOT, "gallery_data.json")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

MIN_QUALITY = 3      # skip "barely usable" gallery shots
MAX_PER_PROJECT = 8  # cap gallery size — keeps pages tight
MAX_WIDTH = 1400

# slug, name, location, category, type, area, status, lead, body
PROJECTS = [
    dict(
        slug="vidorra-commercial-centre", name="Vidorra Commercial Centre",
        location="King Mariout, Egypt", category="Commercial", type="Mixed-Use Complex",
        area="—", status="Built",
        lead="A mixed-use commercial complex anchoring the daily life of King Mariout — a single building that holds the rhythms of a small town.",
        body=[
            "The classic-styled architecture houses two bank branches, a play school, fifteen retail stores, and a constellation of clinics and pharmacies.",
            "Education, commerce, and care — all under one carefully composed roof. The civic gravity of the facade is matched by the functional clarity of the plan."
        ],
    ),
    dict(
        slug="be-sagy-school", name="BE Sagy International School Complex",
        location="Abis, Alexandria", category="Institutional", type="Educational Campus",
        area="26,000 sqm", status="—",
        lead="A 26,000 square-meter educational campus designed to house three schools under one architectural philosophy.",
        body=[
            "A national language school, a British international school, and an American international school — three distinct cultural identities sharing one integrated infrastructure: a full performance theater, a half indoor Olympic swimming pool, and pedagogical spaces designed around the conviction that architecture shapes learning.",
            "The neo-classic envelope provides civic gravity. The interior plan provides the flexibility three pedagogies demand."
        ],
    ),
    dict(
        slug="rakoty-school", name="Rakoty Language National School",
        location="Agami, Alexandria", category="Institutional", type="Educational",
        area="4,500 sqm", status="—",
        lead="A 42-classroom institution wrapped in a glass-and-stone envelope.",
        body=[
            "4,500 square meters in Agami, Alexandria. The neo-classic detailing borrows from the surrounding Mediterranean fabric while the generous fenestration signals a modern educational ethic.",
            "Transparency and permanence, held in a single composition."
        ],
    ),
    dict(
        slug="panacea-2", name="Panacea 2 Compound",
        location="King Mariout, Egypt", category="Residential", type="Mixed-Density Compound",
        area="—", status="—",
        lead="A residential community of 32 townhouse villas, 10 standalone villas, and 82 apartments — designed for the slow rhythms of family life with the conveniences of urban amenity.",
        body=[
            "Anchored by a half Olympic swimming pool and a central clubhouse, the masterplan balances density and privacy, public and intimate.",
            "Three housing typologies. One coherent neighborhood. The architecture treats community as the project — not a byproduct of it."
        ],
    ),
    dict(
        slug="villa-tadros", name="Villa Tadros",
        location="King Mariout, Egypt", category="Residential", type="Private Villa",
        area="650 sqm", status="Built",
        lead="A 650 square-meter modern minimalist villa — where the rendering became the building.",
        body=[
            "Generous horizontal massing, a restrained palette of stone and glass, and carefully composed indoor-outdoor thresholds.",
            "The completed work matches the original drawings with a fidelity that is its own kind of craft."
        ],
    ),
    dict(
        slug="villa-marc", name="Villa Marc",
        location="King Mariout, Egypt", category="Residential", type="Private Villa",
        area="400 sqm", status="—",
        lead="A 400 square-meter contemporary villa shaped by clean geometric lines and a confident sculptural form.",
        body=[
            "Deep overhangs frame interior rooms. A modest footprint reads as generous through proportion and pause.",
            "Modernism here is not a style applied but a discipline kept."
        ],
    ),
    dict(
        slug="villa-merry-land", name="Villa Merry Land",
        location="King Mariout, Egypt", category="Residential", type="Mediterranean Villa",
        area="—", status="—",
        lead="A Mediterranean villa — a quiet tribute to the regional architectural language of the southern shore.",
        body=[
            "Terracotta-tiled roofs, warm stone facades, arched openings, and the patient geometries of vernacular Mediterranean building.",
            "Designed to feel as if it had always been there."
        ],
    ),
    dict(
        slug="afify-palace", name="Afify Palace",
        location="Hawaria, Egypt", category="Residential", type="Palatial Residence",
        area="—", status="—",
        lead="A grand palatial residence built at a ceremonial scale.",
        body=[
            "Classical proportions, ceremonial symmetry, and ornate detailing throughout.",
            "Every threshold is composed; every room earns its place."
        ],
    ),
    dict(
        slug="sea-star-convention", name="Sea Star Convention Centre",
        location="Alexandria, Egypt", category="Hospitality", type="Events & Convention Centre",
        area="—", status="Built",
        lead="A large-scale events and convention centre designed for weddings, conferences, and civic gatherings.",
        body=[
            "The interiors stage moments — pink-lit ceremonial halls, soaring foyers, processional sequences from entry to celebration.",
            "Architecture in service of occasion."
        ],
    ),
    dict(
        slug="royal-wedding-complex", name="Royal Wedding Complex",
        location="Alexandria, Egypt", category="Hospitality", type="Wedding & Event Venue",
        area="—", status="Built",
        lead="An elegant classical wedding venue and event-hall complex.",
        body=[
            "Designed around a simple premise: the most important days deserve the most considered rooms.",
            "Each hall is a stage, and the route between them is choreographed."
        ],
    ),
    dict(
        slug="saint-wanas-church", name="Saint Wanas Church",
        location="Alexandria, Egypt", category="Cultural", type="Religious",
        area="—", status="—",
        lead="A Gothic-inspired church — built to carry the eye, and the attention, upward.",
        body=[
            "Pointed arches, soaring proportions, and stained glass that turns daylight into color.",
            "The structure rises, and everything in it is arranged to rise with it."
        ],
    ),
    dict(
        slug="pope-kirilos-church", name="Pope Kirilos Church",
        location="Aom Zighio, Alexandria", category="Cultural", type="Religious",
        area="—", status="—",
        lead="A Byzantine-style church anchored by a prominent central dome.",
        body=[
            "Sacred geometry inherited from a millennium of liturgical building, executed in contemporary stone and craft.",
            "The dome gathers the room beneath it and holds it still."
        ],
    ),
    dict(
        slug="saint-cyril-medical", name="Saint Cyril Medical Center",
        location="Alexandria, Egypt", category="Commercial", type="Healthcare",
        area="—", status="—",
        lead="A modern medical facility planned around patient comfort and clinical efficiency.",
        body=[
            "Daylight is treated as a primary material. Circulation is treated as a primary design problem.",
            "The architecture is quiet so that the work it shelters can be loud."
        ],
    ),
    dict(
        slug="zafer-landscape", name="Zafer Property Landscape",
        location="Egypt", category="Landscape", type="Private Landscape Commission",
        area="—", status="—",
        lead="A comprehensive landscape commission integrating swimming pools, multi-zone gardens, and an artificial lake into one private-resort experience.",
        body=[
            "Each zone is named and choreographed in relationship to the others — the lake feeds the garden; the garden frames the pool; the pool returns the eye to the lake.",
            "Landscape architecture as a sequence, not a backdrop."
        ],
    ),
    dict(
        slug="agora-bowling", name="Agora Bowling & Gaming Center",
        location="Vidorra Mall", category="Interior", type="Entertainment Venue",
        area="—", status="—",
        lead="A circus-themed entertainment venue combining bowling lanes, gaming areas, and bar/lounge spaces.",
        body=[
            "The interior trades restraint for spectacle — striped canopies, theatrical lighting, an architecture of play.",
            "Designed so that the moment you step in, you know it's not work hours."
        ],
    ),
    dict(
        slug="charles-apartment", name="Charles Apartment",
        location="New Cairo, Egypt", category="Interior", type="Residential Interior",
        area="—", status="—",
        lead="A modern apartment interior with a refined material palette and a single sculptural kitchen at its core.",
        body=[
            "Soft-touch finishes. Open-plan living. Quiet decisions repeated until they accumulate into atmosphere.",
            "Small spaces, considered with care."
        ],
    ),
    dict(
        slug="sandy-wedding-halls", name="Sandy Wedding Halls",
        location="Alexandria, Egypt", category="Interior", type="Event Interiors",
        area="—", status="—",
        lead="A grand wedding venue with layered interiors and a deliberate sense of arrival.",
        body=[
            "Dramatic ceiling lighting. Sequenced thresholds. Designed so guests cross into the hall and feel the day begin.",
            "A room built to meet the occasion it holds."
        ],
    ),
    dict(
        slug="archangel-rafaael", name="Archangel Rafaael Nursing Home",
        location="Agami, Egypt", category="Interior", type="Healthcare Interiors",
        area="—", status="—",
        lead="An ornate interior commission for a nursing home — architecture balancing dignity with warmth.",
        body=[
            "Designed as a residential-scale sanctuary for elder care, with the visual richness of a home that has been lived in for generations.",
            "Care, expressed in materials."
        ],
    ),
]

def crop_image(source_file, t, b, l, r, out_path):
    src = os.path.join(PAGES_DIR, source_file)
    img = Image.open(src).convert("RGB")
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
    cropped.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)
    return cropped.size

with open(GALLERY_JSON, "r", encoding="utf-8") as f:
    GALLERY_DATA = json.load(f)

GALLERIES = {p["slug"]: [] for p in PROJECTS}

print("Cropping gallery images:")
total = 0
for p in PROJECTS:
    slug = p["slug"]
    visuals = GALLERY_DATA.get(slug, [])
    visuals = [v for v in visuals if (v.get("quality") or 0) >= MIN_QUALITY]
    visuals = visuals[:MAX_PER_PROJECT]
    for i, v in enumerate(visuals, start=1):
        out_name = f"{slug}-{i}.jpg"
        out_path = os.path.join(IMG_DIR, out_name)
        try:
            crop_image(
                v["source_file"],
                v["crop_top_pct"], v["crop_bottom_pct"],
                v["crop_left_pct"], v["crop_right_pct"],
                out_path,
            )
            alt = v.get("description") or p["name"]
            GALLERIES[slug].append((out_name, alt))
            total += 1
        except Exception as e:
            print(f"  ! skipped {out_name}: {e}")
    print(f"  {slug:30s} {len(GALLERIES[slug])} images")
print(f"Cropped {total} gallery images total.\n")

CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
--ink:#1A1A1A;--paper:#FAFAF8;--stone:#8B7355;--warm-gray:#B5AFA6;
--light-gray:#E8E5E0;--cloud:#F3F1ED;--deep:#0E0E0E;--slate:#4A4A48;
--serif:'Cormorant Garamond',Georgia,serif;
--sans:'DM Sans','Helvetica Neue',sans-serif;
}
html{scroll-behavior:smooth;font-size:16px}
body{font-family:var(--sans);color:var(--ink);background:var(--paper);
overflow-x:hidden;-webkit-font-smoothing:antialiased;
-webkit-text-size-adjust:100%;text-size-adjust:100%;
-webkit-tap-highlight-color:transparent}
::selection{background:var(--stone);color:var(--paper)}
body::after{content:'';position:fixed;inset:0;pointer-events:none;z-index:9999;opacity:.025;
background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

.nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1rem 3rem;
display:flex;align-items:center;justify-content:space-between;
background:rgba(14,14,14,.92);backdrop-filter:blur(20px)}
.nav-logo img{height:48px}
.nav-links{display:flex;gap:2.5rem;align-items:center}
.nav-links a{font-family:var(--sans);font-size:.75rem;font-weight:400;
letter-spacing:.15em;text-transform:uppercase;color:var(--paper);
text-decoration:none;opacity:.7;transition:opacity .3s}
.nav-links a:hover{opacity:1}
.hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;z-index:100;
width:44px;height:44px;align-items:center;justify-content:center;margin-right:-10px;background:none;border:none}
.hamburger span{display:block;width:24px;height:1.5px;background:var(--paper);transition:all .3s}
.hamburger.active span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}
.hamburger.active span:nth-child(2){opacity:0}
.hamburger.active span:nth-child(3){transform:rotate(-45deg) translate(4px,-4px)}
.mobile-menu{display:none;position:fixed;inset:0;background:var(--deep);z-index:105;
flex-direction:column;align-items:center;justify-content:center;gap:2.5rem;padding:2rem}
.mobile-menu.open{display:flex}
.menu-close{position:absolute;top:1rem;right:1rem;width:44px;height:44px;display:flex;
align-items:center;justify-content:center;background:none;border:none;color:var(--paper);cursor:pointer;transition:color .3s}
.menu-close:hover,.menu-close:active{color:var(--stone)}
.menu-close svg{width:26px;height:26px}
.menu-links{display:flex;flex-direction:column;align-items:center;gap:1.75rem}
.menu-link{font-family:var(--serif);font-size:2rem;font-weight:300;color:var(--paper);
text-decoration:none;opacity:.8;transition:opacity .3s}
.menu-link:hover,.menu-link:active{opacity:1}
.menu-cta{display:flex;flex-direction:column;gap:.85rem;width:100%;max-width:300px}

.reveal{opacity:0;transform:translateY(40px);
transition:opacity .9s cubic-bezier(.4,0,.2,1),transform .9s cubic-bezier(.4,0,.2,1)}
.reveal.visible{opacity:1;transform:translateY(0)}

.project-hero{position:relative;height:90vh;height:90svh;min-height:600px;background:var(--deep);overflow:hidden}
.project-hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.85}
.project-hero::after{content:'';position:absolute;inset:0;
background:linear-gradient(180deg,rgba(14,14,14,.45) 0%,transparent 22%,rgba(14,14,14,.35) 50%,rgba(14,14,14,.8) 78%,rgba(14,14,14,.96) 100%)}
.project-hero-content{position:absolute;bottom:0;left:0;right:0;z-index:2;padding:0 3rem 5rem;
max-width:1400px;margin:0 auto;width:100%;text-shadow:0 1px 18px rgba(14,14,14,.55)}
.back-link{font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;margin-bottom:2rem}
.back-link a{color:rgba(240,237,232,.85);text-decoration:none;transition:color .3s}
.back-link a:hover{color:var(--stone)}
.category-tag{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;color:var(--stone);margin-bottom:1rem;
display:flex;align-items:center;gap:1rem}
.category-tag::before{content:'';width:40px;height:1px;background:var(--stone)}
.project-hero h1{font-family:var(--serif);font-weight:300;font-size:clamp(2.5rem,6vw,5rem);
line-height:1;color:var(--paper);margin-bottom:1rem;max-width:1000px}
.project-hero .subtitle{font-weight:300;font-size:1rem;color:rgba(240,237,232,.5);letter-spacing:.05em}

.meta-strip{background:var(--deep);padding:2rem 3rem;display:grid;grid-template-columns:repeat(4,1fr);
gap:2rem;max-width:1400px;margin:0 auto;border-bottom:1px solid rgba(240,237,232,.06)}
.meta-cell{color:rgba(240,237,232,.6)}
.meta-label{font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;
color:var(--warm-gray);margin-bottom:.5rem}
.meta-value{font-family:var(--serif);font-size:1.4rem;font-weight:300;color:var(--paper);line-height:1.2}

.narrative{background:var(--deep);padding:5rem 3rem;color:var(--paper)}
.narrative-inner{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 2fr;gap:5rem;align-items:start}
.narrative-label{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;color:var(--stone);
display:flex;align-items:center;gap:1rem}
.narrative-label::before{content:'';width:40px;height:1px;background:var(--stone)}
.narrative-body .lead{font-family:var(--serif);font-size:2rem;font-weight:300;
line-height:1.3;margin-bottom:2rem;color:var(--paper)}
.narrative-body p{font-size:1.05rem;font-weight:300;line-height:1.8;color:rgba(240,237,232,.7);margin-bottom:1.25rem}
.project-hero h1{text-wrap:balance}
.narrative-body .lead,.narrative-body p{text-wrap:pretty}

.gallery{padding:5rem 3rem;background:var(--paper)}
.gallery-inner{max-width:1400px;margin:0 auto}
.gallery-label{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;color:var(--stone);
display:flex;align-items:center;gap:1rem;margin-bottom:3rem}
.gallery-label::before{content:'';width:40px;height:1px;background:var(--stone)}
.gallery-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:1rem;align-items:start}
.gallery-grid .gtile{position:relative;overflow:hidden;background:var(--light-gray)}
.gallery-grid .gtile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
transition:transform .6s cubic-bezier(.4,0,.2,1)}
.gallery-grid .gtile:hover img{transform:scale(1.04)}
/* editorial mosaic — full-width features, asymmetric pairs, square pairs */
.g-full{grid-column:span 12;aspect-ratio:16/6}
.g-major{grid-column:span 8;aspect-ratio:5/3}
.g-minor{grid-column:span 4;aspect-ratio:5/6}
.g-square{grid-column:span 6;aspect-ratio:1/1}
.gallery-empty{padding:3rem;text-align:center;color:var(--warm-gray);font-style:italic;font-size:.95rem}

.cta-band{background:var(--deep);color:var(--paper);padding:6rem 3rem;text-align:center}
.cta-inner{max-width:680px;margin:0 auto}
.cta-eyebrow{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;color:var(--stone);margin-bottom:1.25rem}
.cta-title{font-family:var(--serif);font-weight:300;font-size:clamp(1.8rem,3.5vw,2.8rem);
line-height:1.15;margin-bottom:1rem;text-wrap:balance}
.cta-text{font-weight:300;line-height:1.7;color:rgba(240,237,232,.6);margin:0 auto 2.5rem;max-width:480px;text-wrap:pretty}
.cta-actions{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap}
.cta-call,.cta-wa{display:inline-flex;align-items:center;gap:.7rem;text-decoration:none;
padding:1.1rem 2.2rem;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;
font-weight:500;transition:background .3s,color .3s,border-color .3s;min-height:54px}
.cta-call{background:var(--stone);color:var(--paper)}
.cta-call:hover{background:var(--paper);color:var(--deep)}
.cta-wa{background:transparent;color:var(--paper);border:1px solid rgba(240,237,232,.3)}
.cta-wa:hover{border-color:var(--stone);background:rgba(139,115,85,.15)}
.cta-call svg,.cta-wa svg{width:18px;height:18px;flex-shrink:0}
.cta-phone{margin-top:1.25rem;font-size:.8rem;letter-spacing:.05em;color:rgba(240,237,232,.42)}

.to-top{position:fixed;bottom:1.5rem;right:1.5rem;z-index:90;width:46px;height:46px;
display:flex;align-items:center;justify-content:center;background:rgba(14,14,14,.7);
backdrop-filter:blur(8px);color:var(--paper);border:1px solid rgba(240,237,232,.18);
cursor:pointer;opacity:0;visibility:hidden;transform:translateY(12px);
transition:opacity .4s,transform .4s,background .3s,border-color .3s}
.to-top.show{opacity:1;visibility:visible;transform:translateY(0)}
.to-top:hover{background:var(--stone);border-color:var(--stone)}
.to-top svg{width:18px;height:18px}

.proj-nav{padding:4rem 3rem;background:var(--cloud);
display:grid;grid-template-columns:1fr auto 1fr;gap:2rem;align-items:center;border-top:1px solid var(--light-gray)}
.proj-nav a{text-decoration:none;color:var(--ink);transition:color .3s}
.proj-nav a:hover{color:var(--stone)}
.proj-nav .prev{justify-self:start}
.proj-nav .all{justify-self:center;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase}
.proj-nav .next{justify-self:end;text-align:right}
.proj-nav-direction{font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:var(--warm-gray);margin-bottom:.3rem}
.proj-nav-name{font-family:var(--serif);font-size:1.3rem;font-weight:400}

.footer{background:var(--deep);padding:3rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1.5rem}
.footer-left{display:flex;align-items:center;gap:2rem}
.footer-logo img{height:24px}
.footer-copy,.footer-right{font-size:.7rem;color:rgba(240,237,232,.3);letter-spacing:.05em}

@media(max-width:1024px){
  .nav{padding:1rem 2rem}
  .narrative-inner{grid-template-columns:1fr;gap:2rem}
  .meta-strip{grid-template-columns:repeat(2,1fr);padding:2rem}
  .gallery-grid{gap:.85rem}
}
@media(max-width:768px){
  .nav{padding:.75rem max(1.25rem,env(safe-area-inset-right)) .75rem max(1.25rem,env(safe-area-inset-left))}
  .nav-logo img{height:52px}
  .nav-links{display:none}
  .hamburger{display:flex}
  .project-hero{height:70vh;height:70svh;min-height:500px}
  .project-hero-content{padding:0 1.25rem 3rem}
  .back-link{margin-bottom:1.25rem;font-size:.65rem}
  .category-tag{margin-bottom:.75rem;font-size:.65rem}
  .category-tag::before{width:24px}
  .project-hero h1{font-size:clamp(2rem,8vw,3rem);margin-bottom:.75rem}
  .project-hero .subtitle{font-size:.9rem}
  .meta-strip{grid-template-columns:1fr;padding:1.5rem 1.25rem;gap:1.25rem}
  .meta-value{font-size:1.2rem}
  .narrative{padding:3rem 1.25rem}
  .narrative-inner{gap:1.5rem}
  .narrative-body .lead{font-size:1.4rem;margin-bottom:1.25rem}
  .narrative-body p{font-size:.95rem}
  .gallery{padding:3rem 1.25rem}
  .gallery-label{margin-bottom:2rem}
  .gallery-grid{grid-template-columns:repeat(2,1fr);gap:.6rem}
  .gallery-grid .gtile{aspect-ratio:4/5}
  .g-full{grid-column:span 2;aspect-ratio:16/10}
  .g-major,.g-minor,.g-square{grid-column:span 1}
  .cta-band{padding:4rem 1.25rem}
  .cta-actions{flex-direction:column}
  .cta-call,.cta-wa{width:100%;justify-content:center}
  .proj-nav{padding:2.5rem 1.25rem;grid-template-columns:1fr;text-align:center;gap:1.5rem}
  .proj-nav .prev,.proj-nav .next{justify-self:center;text-align:center}
  .proj-nav-name{font-size:1.1rem}
  .footer{flex-direction:column;text-align:center;gap:1rem;padding:2rem 1.25rem}
  .footer-left{flex-direction:column;gap:.75rem}
}
@media(max-width:480px){
  .project-hero{min-height:440px}
  .project-hero h1{font-size:clamp(1.9rem,9vw,2.6rem)}
  .narrative-body .lead{font-size:1.3rem}
}

/* Touch devices: disable decorative hover-zoom, add tap feedback */
@media(hover:none){
  .gallery-grid .gtile:hover img{transform:none}
  .gallery-grid .gtile:active img{transform:scale(1.03)}
  .menu-link:active{color:var(--stone)}
  .proj-nav a:active{color:var(--stone)}
}

/* Respect users who prefer reduced motion */
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;
    transition-duration:.001ms!important;scroll-behavior:auto!important}
  .reveal{opacity:1!important;transform:none!important}
}
"""

NAV_HTML = """
<nav class="nav">
  <a class="nav-logo" href="../index.html"><img src="../brand/logo-lockup-dark.svg" alt="Isaac Architects"></a>
  <div class="nav-links">
    <a href="../index.html#work">Work</a>
    <a href="../index.html#about">Studio</a>
    <a href="../index.html#approach">Approach</a>
    <a href="../index.html#contact">Contact</a>
  </div>
  <button class="hamburger" id="hamburger" aria-label="Menu" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <button class="menu-close" id="menuClose" aria-label="Close menu">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>
  </button>
  <nav class="menu-links">
    <a class="menu-link" href="../index.html#work">Work</a>
    <a class="menu-link" href="../index.html#about">Studio</a>
    <a class="menu-link" href="../index.html#approach">Approach</a>
    <a class="menu-link" href="../index.html#contact">Contact</a>
  </nav>
  <div class="menu-cta">
    <a class="cta-call" href="tel:+201274348575">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z"/></svg>
      Call the studio
    </a>
    <a class="cta-wa" href="https://wa.me/201274348575?text=Hi%20Isaac%20Architects%2C%20I'd%20like%20to%20talk%20about%20a%20project." target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.625.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.247-.694.247-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
      WhatsApp
    </a>
  </div>
</div>
<button class="to-top" id="toTop" aria-label="Back to top">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>
"""

MENU_SCRIPT = """
<script>
(function(){
  var obs=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target);}
  });},{threshold:.1,rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(function(el){obs.observe(el);});

  var t=document.getElementById('toTop');
  if(t){
    var onScroll=function(){t.classList.toggle('show',window.scrollY>600);};
    window.addEventListener('scroll',onScroll,{passive:true});onScroll();
    t.addEventListener('click',function(){
      var rm=window.matchMedia('(prefers-reduced-motion:reduce)').matches;
      window.scrollTo({top:0,behavior:rm?'auto':'smooth'});
    });
  }

  var h=document.getElementById('hamburger'),m=document.getElementById('mobileMenu'),
      c=document.getElementById('menuClose');
  if(!h||!m)return;
  function setMenu(open){
    m.classList.toggle('open',open);
    document.body.style.overflow=open?'hidden':'';
    h.setAttribute('aria-expanded',open?'true':'false');
  }
  h.addEventListener('click',function(){setMenu(true);});
  if(c)c.addEventListener('click',function(){setMenu(false);});
  m.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click',function(){setMenu(false);});
  });
})();
</script>
"""

FOOTER_HTML = """
<footer class="footer">
  <div class="footer-left">
    <div class="footer-logo"><img src="../brand/logo-lockup-dark.svg" alt="Isaac Architects"></div>
    <div class="footer-copy">&copy; 2024 Isaac Architects. All rights reserved.</div>
  </div>
  <div class="footer-right">Founded by Eng. Mina Kamal Isaac &middot; Alexandria, Egypt</div>
</footer>
"""


def gallery_shapes(n):
    """Editorial mosaic rhythm: full-width opener, then alternating asymmetric
    pairs (major+minor, sides swapping) and square pairs, with periodic
    full-width breaks. Every row fills 12 cols (and pairs cleanly into 2 cols
    on mobile); a leftover single tile becomes a full-width band."""
    recipes = [["g-full"], ["g-major", "g-minor"], ["g-square", "g-square"], ["g-minor", "g-major"]]
    shapes, i, r = [], 0, 0
    while i < n:
        recipe = recipes[r % len(recipes)]
        if len(recipe) <= n - i:
            shapes += recipe
            i += len(recipe)
        else:
            shapes.append("g-full")  # lone trailing tile -> full-width band
            i += 1
        r += 1
    return shapes


def render_gallery(slug):
    items = GALLERIES.get(slug, [])
    if not items:
        return '<div class="gallery-empty">Additional project imagery coming soon.</div>'
    shapes = gallery_shapes(len(items))
    out = ['<div class="gallery-grid">']
    for (fname, alt), shape in zip(items, shapes):
        out.append(f'<figure class="gtile {shape} reveal"><img src="../images/{fname}" alt="{escape(alt)}" loading="lazy"></figure>')
    out.append('</div>')
    return "\n".join(out)


def render_page(p, prev_p, next_p):
    body_html = "\n".join(f'<p>{escape(par)}</p>' for par in p["body"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(p['name'])} — Isaac Architects</title>
<meta name="description" content="{escape(p['lead'])}">
<link rel="canonical" href="https://mina-geez.github.io/isaac-architects/projects/{p['slug']}.html">
<link rel="icon" type="image/svg+xml" href="../brand/logo-mark.svg">

<meta property="og:type" content="article">
<meta property="og:url" content="https://mina-geez.github.io/isaac-architects/projects/{p['slug']}.html">
<meta property="og:title" content="{escape(p['name'])} — Isaac Architects">
<meta property="og:description" content="{escape(p['lead'])}">
<meta property="og:image" content="https://mina-geez.github.io/isaac-architects/images/{p['slug']}.jpg">
<meta property="og:site_name" content="Isaac Architects">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(p['name'])}">
<meta name="twitter:description" content="{escape(p['lead'])}">
<meta name="twitter:image" content="https://mina-geez.github.io/isaac-architects/images/{p['slug']}.jpg">

<meta name="theme-color" content="#0E0E0E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Sans:ital,wght@0,200;0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

{NAV_HTML}

<header class="project-hero">
  <img src="../images/{p['slug']}.jpg" alt="{escape(p['name'])}">
  <div class="project-hero-content">
    <div class="back-link"><a href="../index.html#work">&larr; All Projects</a></div>
    <div class="category-tag">{escape(p['category'])}</div>
    <h1>{escape(p['name'])}</h1>
    <div class="subtitle">{escape(p['location'])}</div>
  </div>
</header>

<section class="meta-strip">
  <div class="meta-cell reveal"><div class="meta-label">Location</div><div class="meta-value">{escape(p['location'])}</div></div>
  <div class="meta-cell reveal" style="transition-delay:.08s"><div class="meta-label">Type</div><div class="meta-value">{escape(p['type'])}</div></div>
  <div class="meta-cell reveal" style="transition-delay:.16s"><div class="meta-label">Area</div><div class="meta-value">{escape(p['area'])}</div></div>
  <div class="meta-cell reveal" style="transition-delay:.24s"><div class="meta-label">Status</div><div class="meta-value">{escape(p['status'])}</div></div>
</section>

<section class="narrative">
  <div class="narrative-inner">
    <div class="narrative-label reveal">Project</div>
    <div class="narrative-body reveal" style="transition-delay:.1s">
      <p class="lead">{escape(p['lead'])}</p>
      {body_html}
    </div>
  </div>
</section>

<section class="gallery">
  <div class="gallery-inner">
    <div class="gallery-label reveal">Gallery</div>
    {render_gallery(p['slug'])}
  </div>
</section>

<section class="cta-band">
  <div class="cta-inner">
    <div class="cta-eyebrow reveal">Work with us</div>
    <h2 class="cta-title reveal" style="transition-delay:.05s">Have a project in mind?</h2>
    <p class="cta-text reveal" style="transition-delay:.1s">Tell us what you need the space to do. Every project we take on begins with a conversation.</p>
    <div class="cta-actions reveal" style="transition-delay:.15s">
      <a class="cta-call" href="tel:{PHONE}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z"/></svg>
        Call the studio
      </a>
      <a class="cta-wa" href="https://wa.me/{WHATSAPP}?text={quote(f"Hi Isaac Architects, I'm interested in a project like {p['name']}.")}" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.625.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.247-.694.247-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
        WhatsApp
      </a>
    </div>
    <div class="cta-phone reveal" style="transition-delay:.2s">{PHONE_DISPLAY}</div>
  </div>
</section>

<nav class="proj-nav reveal">
  <a class="prev" href="{prev_p['slug']}.html">
    <div class="proj-nav-direction">&larr; Previous</div>
    <div class="proj-nav-name">{escape(prev_p['name'])}</div>
  </a>
  <a class="all" href="../index.html#work">All Projects</a>
  <a class="next" href="{next_p['slug']}.html">
    <div class="proj-nav-direction">Next &rarr;</div>
    <div class="proj-nav-name">{escape(next_p['name'])}</div>
  </a>
</nav>

{FOOTER_HTML}
{MENU_SCRIPT}
</body>
</html>
"""


for i, p in enumerate(PROJECTS):
    prev_p = PROJECTS[(i - 1) % len(PROJECTS)]
    next_p = PROJECTS[(i + 1) % len(PROJECTS)]
    out = os.path.join(OUT_DIR, f"{p['slug']}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(render_page(p, prev_p, next_p))

print(f"Generated {len(PROJECTS)} project pages in {OUT_DIR}")
