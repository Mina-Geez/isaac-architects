---
description: Add a new standalone page or page type (journal, team, …)
---
Add a new page to the content engine.

1. Create `content/pages/<slug>.md` with TOML frontmatter (`title`, `description`, optional `template = "page"`) and a Markdown body.
2. If it needs its own layout, create `templates/<type>.html` (start by copying `templates/page.html`) and set `template = "<type>"` in the frontmatter.
3. Wire page rendering into `build.py` if not already present: load `content/pages/*.md`, render each through its template to `<slug>.html` at the repo root, and add it to the sitemap list.
4. Run `python build.py`, preview, then `/publish`.

Note: project pages and the home page are fully wired today; generic `content/pages/` rendering is the documented extension point (see `docs/superpowers/specs/2026-06-14-content-engine-design.md`).
