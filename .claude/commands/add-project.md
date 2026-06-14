---
description: Add a new project to the Isaac Architects site
---
Add a new project to the content engine.

1. Ask for: **name, location, category** (Residential / Commercial / Institutional / Hospitality / Interior / Cultural / Landscape), **type, area** (or `—`), **status** (`Built` or `—`), a one-line **lead**, and the **body** paragraphs. Also where it sits in the portfolio order and whether it's a **featured** (wide) card on the home grid.
2. Derive a kebab-case **slug**. Create `content/projects/<slug>/index.md` with TOML frontmatter:
   ```
   +++
   name = "…"
   location = "…"
   category = "…"
   type = "…"
   area = "…"
   status = "…"
   lead = "…"
   hero = "hero.jpg"
   order = <n>
   featured = false
   draft = false
   [[gallery]]
   src = "01.jpg"
   alt = "descriptive alt text"
   +++

   First body paragraph.

   Second body paragraph.
   ```
   Bump the `order` of later projects if inserting in the middle.
3. Ask me to drop the hero image as `content/projects/<slug>/hero.jpg` and gallery images as `01.jpg`, `02.jpg`, … in that folder (or give paths and copy them in). Add one `[[gallery]]` entry per image.
4. Run `python build.py`. The build validates content and fails loudly on missing fields/images.
5. Optionally screenshot the new page to preview. Then tell me to run `/publish`.
