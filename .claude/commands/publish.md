---
description: Build the site and deploy it (commit + push)
---
Build and publish the Isaac Architects site.

1. Run `python build.py`.
2. Run `python -m pytest -q` (engine tests must pass).
3. If a parity baseline exists, run `python tools/parity_diff.py`.
4. Stage everything (content + build output) and commit + push to `main` using the one-shot git author override (CLAUDE.md):
   ```
   git add -A
   git -c user.name=Mina-Geez -c user.email=mina-geez@users.noreply.github.com commit -m "…"
   git push origin main
   ```
5. Cloudflare redeploys automatically from `main`.
