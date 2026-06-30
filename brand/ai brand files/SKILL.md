---
name: isaac-architects-brand-guidelines
description: Applies the official Isaac Architects brand identity — calligraphic signature mark, restrained palette, Cormorant Garamond + DM Sans typography, hairline rule treatments, and editorial voice — to any artifact, document, presentation, proposal, email, HTML page, React component, or visual output. Use this skill whenever creating or styling ANY visual deliverable for Isaac Architects including portfolio pages, proposals, presentations, websites, landing pages, email signatures, social media assets, documents, business cards, letterheads, signage mockups, or any output that should carry the Isaac Architects look-and-feel. Also trigger when mentions of "Isaac", "Isaac Architects", "Isaac brand", "Isaac style", "the architect's brand", "the firm's identity", "@isaac_architects", or similar references occur. The brand is built around restraint, material honesty, and the signature as the central mark — every output must respect that hierarchy.
---

# Isaac Architects — Brand Identity System

## Overview

Isaac Architects is a high-end architectural practice. The brand identity is built around a single calligraphic signature mark — "Isaac" — paired with the tagline "ARCHITECTS" set in DM Sans. The visual language is restrained, material-honest, and editorial. The signature signals personal authorship; the structured tagline signals craft and precision.

Every visual output must follow these specifications. The brand philosophy is **measured restraint**: bold typography earned through proportion, generous whitespace, and confident use of a small palette. No decorative elements. The signature is the brand; everything else supports it.

**Positioning**: An Alexandria, Egypt studio working across residential, commercial, institutional, hospitality, cultural, interior, and landscape architecture
**Founder**: Eng. Mina Kamal Isaac
**Voice**: Measured, personal, assured
**Website**: isaacarchitects.com
**Social**: @isaac_architects

For the full rendered brand system (7-page PDF), see `references/brand-system.pdf`.
SVG logo files live in `assets/`.

---

## Logo System

The logo consists of three components stacked vertically on a shared vertical axis:

1. **Mark** — "Isaac" in custom calligraphic script (`logo-mark.svg`)
2. **Rule** — hairline horizontal line, 0.75px weight, full opacity
3. **Tagline** — "ARCHITECTS" in DM Sans 200 (ExtraLight), 13–15px letter-spacing, uppercase

### Lockups

| Variant | File | Use Case |
|---------|------|----------|
| Primary Light | `assets/logo-lockup-light.svg` | Default — dark mark on light backgrounds |
| Primary Dark | `assets/logo-lockup-dark.svg` | Reversed — light mark on dark backgrounds |
| Mark Only | `assets/logo-mark.svg` | Favicon, watermark, small-scale applications |

### Rule Specifications

The hairline rule is the most-fiddled-with element. These are the final specs — do not deviate:

- **Weight**: 0.75px
- **Opacity**: 100% (full opacity, not faded)
- **Length**: ~60% of the lockup width, max ~240–280px at standard sizes
- **Spacing**: 14px above and 14px below at standard sizes (18px at hero scale)
- **Alignment**: horizontally centered
- **Color**: matches the mark color (Ink on light, Paper on dark)

The rule is proportioned to the **negative space between the script and the tagline**, not to either word's width. It establishes the *interval* between elements. Avoid:

- Curved or wavy lines
- Full-lockup-width spans (creates visual stuttering with "ARCHITECTS")
- Faded opacity (reads apologetic)
- Heavy weights above 1px (reads as a divider, not a rule)

### Clear Space

Minimum clear space around the lockup equals the cap height of "ARCHITECTS". Never crowd the mark.

### Minimum Sizes

- **Full lockup**: 80px wide minimum (web), 25mm wide minimum (print)
- **Mark only**: 32px wide minimum (favicons), 12mm wide minimum (print)

Below these sizes, use mark-only.

---

## Color Palette

The palette is drawn from the architect's desk — ink on paper, brushed stone, pencil graphite. Warm neutrals only. Never introduce a color outside this list.

### Primary Colors

| Name         | Role                          | Hex       | RGB            |
|--------------|-------------------------------|-----------|----------------|
| Ink          | Primary text and mark         | `#1A1A1A` | 26, 26, 26     |
| Deep         | Dark backgrounds              | `#0E0E0E` | 14, 14, 14     |
| Paper        | Default background            | `#FAFAF8` | 250, 250, 248  |

### Accent

| Name         | Role                          | Hex       | RGB            |
|--------------|-------------------------------|-----------|----------------|
| Stone        | Single accent color           | `#8B7355` | 139, 115, 85   |

Stone is used sparingly — for section numbers, small detail elements, and accent backgrounds. Never for body text or large fills.

### Neutrals

| Name         | Role                          | Hex       | RGB            |
|--------------|-------------------------------|-----------|----------------|
| Warm Gray    | Secondary text, metadata      | `#B5AFA6` | 181, 175, 166  |
| Light Gray   | Borders, hairlines, dividers  | `#E8E5E0` | 232, 229, 224  |
| Cloud        | Tinted alternate background   | `#F3F1ED` | 243, 241, 237  |
| Slate        | Dark mode secondary text      | `#4A4A48` | 74, 74, 72     |

### CSS Variables

```css
:root {
  --ink: #1A1A1A;
  --deep: #0E0E0E;
  --paper: #FAFAF8;
  --stone: #8B7355;
  --warm-gray: #B5AFA6;
  --light-gray: #E8E5E0;
  --cloud: #F3F1ED;
  --slate: #4A4A48;
}
```

### Usage Rules

- **Ink on Paper** is the default combination — use it 80% of the time
- **Deep backgrounds** for editorial sections, philosophy statements, hero alternates
- **Stone accent** only for section numbers (sec-num style), small dividers, and on-brand callouts — never as a primary color
- **Light Gray hairlines** for dividers, card borders, page footer rules — always at 1px
- Never gradients. Never shadows above 0.05 opacity. Never colored backgrounds outside this palette.

---

## Typography

Two typefaces, distinct roles. They never compete. The logo is an image mark, not a typeface — never typeset "Isaac" in any font as a substitute for the SVG mark.

### Display — Cormorant Garamond

Used for: page titles, section headlines, editorial pull quotes, philosophical statements.

- **Weights available**: 300 (Light), 400 (Regular), 500 (Medium), 600 (SemiBold)
- **Italic variants**: 300, 400 (use sparingly for editorial emphasis)
- **Default weight**: 300
- **Line height**: 1.2–1.35

**Google Fonts import**:
```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
```

**Common sizes**:
- Page titles: 36px / weight 300
- Section headlines: 24px / weight 400
- Pull quotes: 20px italic / weight 300
- Editorial captions: 16px / weight 400

### Body — DM Sans

Used for: body copy, navigation, metadata, captions, taglines, all interface text.

- **Weights available**: 200 (ExtraLight), 300 (Light), 400 (Regular), 500 (Medium)
- **Italic variants**: 300 (use only for editorial emphasis)
- **Default weight**: 300
- **Line height**: 1.7–1.9 for body, 1.0 for tags/labels

**Google Fonts import**:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,200;0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">
```

**Common sizes**:
- Body copy: 14px / weight 300 / line-height 1.7
- Navigation: 12px / weight 400 / letter-spacing 2px / uppercase
- Tagline ("ARCHITECTS"): 13–15px / weight 200 / letter-spacing 13–15px / uppercase
- Section numbers ("01 — Logo System"): 10px / weight 400 / letter-spacing 5px / uppercase / Stone color
- Small metadata: 9–10px / weight 400 / letter-spacing 2–4px / uppercase / Warm Gray color

### Combined Font Import (Recommended)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,200;0,300;0,400;0,500;1,300&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
```

### Typography Rules

- Body copy never below 13px on web, 9pt in print
- Letter-spacing only used on uppercase text (taglines, navigation, section numbers)
- Never mix more than two weights of the same typeface in a single element
- Italics reserved for editorial pull quotes and emphasis — not for body styling
- Never use serif typefaces other than Cormorant Garamond
- Never use sans-serifs other than DM Sans

---

## Layout Principles

### Grid

Mobile-first responsive grid. Breakpoints at 600px (tablet), 768px (small desktop), 1200px (full desktop).

### Whitespace

The brand reads as luxury through whitespace, not decoration. Default to **more breathing room than feels comfortable** — then add 20%.

- Section padding: 80–120px vertical on desktop, 48–64px on mobile
- Content max-width: 1200px on desktop, full-bleed on mobile
- Paragraph max-width: 60ch (about 420px at 14px) for readability

### Section Structure

A canonical Isaac Architects section follows this pattern:

```
[Section Number — small Stone label, letter-spaced]
[Section Title — Cormorant Garamond 300, large]
[Description paragraph — DM Sans 300, max 420px wide]
[Content grid or visual]
[Footer rule + metadata if applicable]
```

### Image Treatment

- Photography is **always editorial in tone** — architectural, restrained, no people in frame for hero shots
- Black-and-white or muted color only — never saturated
- Overlay darkening at 5–30% opacity when text sits over images
- Aspect ratios: 4:3, 3:2, 16:9, 1:1 — never irregular

---

## Voice & Tone

The brand voice matches the signature — personal, considered, unhurried.

### Three Traits

1. **Measured** — Say less, mean more. Every word earns its place. No filler, no jargon, no industry clichés.
2. **Personal** — First person. Direct address. Architecture is a relationship between people and space.
3. **Assured** — Confident without arrogance. State positions clearly. Don't hedge or oversell.

### Voice Examples

**Yes:**
> "We design for permanence — structures that age with character, serve their inhabitants faithfully, and carry meaning beyond their materials."

> "Every project starts with a conversation. We study the site, the climate, the way you move through a day."

> "Design with intention. Build with integrity."

**No:**
> "Our award-winning team leverages cutting-edge design solutions to deliver innovative spaces that exceed client expectations." (corporate jargon, self-praise)

> "🏛️ Excited to share our latest project! ✨" (casual, emoji-laden)

> "At Isaac Architects, we believe architecture is more than just buildings..." (cliché opener)

### Editorial Tone

Captions, taglines, and metadata follow the same restraint as the visual system:

- Section numbers: "01 — Logo System" (not "Section 1" or "Chapter One")
- Project metadata: "Residential / King Mariout, Egypt / 2024" (not "Beautiful Modern Residential Project in King Mariout")
- Image captions: short, factual, never explaining the obvious

---

## Component Specifications

### Section Numbers (sec-num)

```css
.sec-num {
  font-family: 'DM Sans', sans-serif;
  font-size: 10px;
  letter-spacing: 5px;
  text-transform: uppercase;
  color: var(--warm-gray);  /* or var(--stone) for emphasis */
  margin-bottom: 32px;
}
```

### Hairline Rule

```css
.hero-rule {
  width: 60%;
  max-width: 240px;
  height: 0.75px;
  background: var(--ink);  /* or var(--paper) on dark backgrounds */
  margin: 14px auto;
  opacity: 1;
}

@media (min-width: 768px) {
  .hero-rule {
    max-width: 280px;
    margin: 18px auto;
  }
}
```

### Page Footer (within brand system documents)

```css
.page-footer {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid var(--light-gray);
  display: flex;
  justify-content: space-between;
  font-family: 'DM Sans', sans-serif;
  font-size: 8px;
  color: var(--warm-gray);
  letter-spacing: 1px;
}
```

### Tagline ("ARCHITECTS")

```css
.tagline {
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 200;
  letter-spacing: 13px;
  text-transform: uppercase;
  color: var(--ink);  /* matches mark color */
}

/* At hero scale */
.hero .tagline {
  font-size: 17px;
  letter-spacing: 15px;
}
```

---

## Application Standards

### Business Cards

- 85mm × 55mm (standard EU) or 3.5in × 2in (US)
- Front: lockup centered, contact details aligned bottom-right
- Back: Deep (#0E0E0E) background, lockup centered in Paper (#FAFAF8)
- Paper stock: uncoated, 350–400 gsm

### Letterhead

- A4 / US Letter
- Lockup top-left, contact details top-right
- 14px Cormorant Garamond date below header
- 28mm top/bottom margins, 24mm left/right
- Footer: full-width hairline + legal info in 7px DM Sans / Warm Gray

### Proposals & Presentations

Multi-page proposals and presentation decks (A4 pages) are the firm's primary new-business deliverable. They follow the same restraint as every other surface. These conventions were settled during production of the first major proposal (White Yard) — follow them rather than re-deriving each time.

**Covers (front and back)**

- Use the **official one-piece lockup** (mark + hairline rule + "ARCHITECTS") as a single locked unit on *both* covers. Never reassemble the lockup from separate pieces or retype "ARCHITECTS" beside the mark — cover-to-cover consistency is the point.
- The front cover carries a **full-bleed hero image** — architectural, editorial, darkened 15–30% behind any text.
- Keep the cover lockup quiet: **~78px tall** is the tested size on an A4 cover. Resist going larger.

**Front-cover authorship credit** — the principal is named beneath the title block:

```html
<div style="font-family:'DM Sans',sans-serif;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:var(--stone);margin-bottom:6px">Designed by</div>
<div style="font-family:'Cormorant Garamond',serif;font-size:19px;font-weight:400;color:var(--paper);line-height:1.15">Mina K. Isaac</div>
<div style="font-family:'DM Sans',sans-serif;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:rgba(240,237,232,0.45);margin-top:7px">isaacarchitects.com</div>
```

**Back cover**

- Lead with an **enlarged closing statement** (Cormorant Garamond 300, generous size) — the back cover is a deliberate full stop, not a footer.
- Close with a **four-column contact band** on a Deep background. An earlier version carried a phone "subtext" line and a separate Social column; both were dropped for restraint. **No social column — four columns only.**

Contact band — per column: Stone micro-label / Cormorant value / one faint italic descriptor:

```html
<div style="border-top:1px solid rgba(240,237,232,0.25);padding-top:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:8mm">
  <!-- one block per column -->
  <div>
    <div style="font-family:'DM Sans',sans-serif;font-size:8px;letter-spacing:2.5px;text-transform:uppercase;color:var(--stone);margin-bottom:10px">Studio</div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:15px;font-weight:400;color:var(--paper);line-height:1.4">Isaac Architects</div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:11px;font-style:italic;color:rgba(240,237,232,0.65);margin-top:3px">Alexandria, Egypt</div>
  </div>
</div>
```

The four columns, in order:

| Label | Value | Descriptor |
|-------|-------|------------|
| Studio | Isaac Architects | *Alexandria, Egypt* |
| Web | isaacarchitects.com | *Selected Works* |
| Correspondence | mina@isaacarchitects.com | *New Project Enquiries* |
| Telephone | +20 127 434 8575 | *Direct Line* |

**Page footer** — project attribution left, page number `NN / NN` right, in the standard `.page-footer` style (8px DM Sans / Warm Gray).

**Typographic polish** — no orphan words (a lone word wrapping onto its own line) in titles or statements; tighten the measure or rebalance the line instead.

### Social Media

- Profile mark: `assets/logo-mark.svg`, centered on Paper background
- Posts: editorial captions in DM Sans 300, hashtags minimal (3–5 maximum)
- Story templates: dark Deep background, light Paper text
- Image filters: subtle desaturation, never saturated/HDR

### Email Signatures

```
Eng. Mina Kamal Isaac
Founder

Isaac Architects
+20 127 434 8575
mina@isaacarchitects.com
isaacarchitects.com
```

- Name in Cormorant Garamond 400
- Title in DM Sans 200, letter-spaced, uppercase, Stone color
- Contact in DM Sans 300, Ink
- No graphics, no social icons, no taglines

### Environmental Signage

- Three-dimensional applications: mark in raised metal (bronze, brushed steel) on natural materials (travertine, walnut, concrete)
- Mark and tagline always together at architectural scale
- Reference the lobby installation in `references/brand-system.pdf` (page 5)

---

## What NOT to Do

- ✗ Don't typeset "Isaac" in any font as a substitute for the SVG mark
- ✗ Don't apply drop shadows, outlines, gradients, or effects to the logo
- ✗ Don't rotate, stretch, compress, or animate the logo
- ✗ Don't place the logo on busy photography without sufficient overlay darkening
- ✗ Don't introduce colors outside the palette
- ✗ Don't use the rule at heavy weights, curved paths, or faded opacity
- ✗ Don't mix more than two typefaces (Cormorant Garamond + DM Sans only)
- ✗ Don't use emoji, ornaments, decorative bullets, or graphical embellishments
- ✗ Don't write in corporate marketing voice — measured, personal, assured only
- ✗ Don't crop or modify the photographic mockups in `references/brand-system.pdf`

---

## When to Apply This Skill

Trigger this skill whenever:

- Creating or styling any deliverable explicitly for Isaac Architects
- The phrase "Isaac", "Isaac Architects", "the architecture firm", or related terms appears
- Mockups, proposals, presentations, websites, or marketing collateral are being built for the firm
- Brand consistency is needed across multiple touchpoints
- Reference is made to "the architect's brand" in context of this firm

When in doubt about brand application, refer to `references/brand-system.pdf` — the 7-page system document is the authoritative reference. SVG logo files live in `assets/` and should be used directly rather than recreated.
