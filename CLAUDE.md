# Isaac Architects — project notes

Rebrand of **IDEA Designs** (Eng. Mina Kamal Isaac, Alexandria, Egypt) into **Isaac Architects**. This directory holds the brand system and the single-file portfolio website.

## Files

- `isaac-architects-website.html` — the deliverable. Single-file HTML, links to `brand/*.svg`. Contains 18 real projects extracted from the client PDFs, organized by category.
- `brand/logo-mark.svg`, `brand/logo-lockup-dark.svg`, `brand/logo-lockup-light.svg` — official logos. **Preserve exactly.** Reference them from the HTML rather than re-inlining (inlining bloats the file from ~25 KB to ~1.2 MB).
- `brand/isaac-architects-brand-system.pdf` — brand guidelines.
- `Client input - previous projects/` — three image-based source PDFs from the client.
- `pdf_pages/` — all 88 PDF pages pre-rendered to 2× PNGs for visual reading.

## Brand constraints

- **Palette** (CSS vars, do not invent new ones):
  `--ink:#1A1A1A`, `--paper:#FAFAF8`, `--stone:#8B7355` (accent), `--warm-gray:#B5AFA6`, `--light-gray:#E8E5E0`, `--cloud:#F3F1ED`, `--deep:#0E0E0E`, `--slate:#4A4A48`.
- **Typography**: Cormorant Garamond (serif headings) + DM Sans (body), both from Google Fonts.
- **Contact info** (real, don't change): `ideadesigns.arch@gmail.com`, `+20 127 434 8575`, `+20 120 383 4437`.

## Working with the PDFs

Source PDFs have no text layer. Don't try to Read them directly or extract text via PowerShell — both produce empty output. Use the pre-rendered PNGs in `pdf_pages/`, or re-render new files with pymupdf at 2× resolution.

## Environment

Windows 11, Git Bash + PowerShell, no `jq` installed. Shell scripts that need JSON parsing should use Python (3.14 on PATH) or Node, not bash + jq.
