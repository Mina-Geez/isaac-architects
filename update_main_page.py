"""1. Remove the redundant 'Featured Project' section (BE Sagy is already in the grid)
2. Convert project-card <div>s to clickable <a> tags linking to projects/<slug>.html
3. Update .project-card CSS so anchor styling matches the prior div behavior."""
import re

HTML = r"C:\Users\test-\OneDrive\Desktop\Isaac Architects\isaac-architects-website.html"

with open(HTML, "r", encoding="utf-8") as f:
    src = f.read()

# 1. Remove the entire featured section
src = re.sub(
    r"<section class=\"featured\">.*?</section>\s*",
    "",
    src,
    count=1,
    flags=re.DOTALL,
)

# 2. Update .project-card CSS — add display:block, color:inherit, text-decoration:none
src = src.replace(
    ".project-card{position:absolute;inset:0;cursor:pointer;",
    ".project-card{position:absolute;inset:0;cursor:pointer;",  # no-op safety
)
src = src.replace(
    ".project-card{position:relative;overflow:hidden;cursor:pointer;\naspect-ratio:4/5;background:var(--deep)}",
    ".project-card{position:relative;overflow:hidden;cursor:pointer;\naspect-ratio:4/5;background:var(--deep);display:block;color:inherit;text-decoration:none}"
)

# 3. Each project card → anchor with href.
# Match by trailing <img src="images/SLUG.jpg"> inside the card to capture slug.
def card_to_anchor(match):
    head = match.group(1)        # `<div class="project-card ... data-category="...">`  + opening
    body = match.group(2)        # full inner contents
    slug_match = re.search(r'src="images/([a-z0-9-]+)\.jpg"', body)
    if not slug_match:
        return match.group(0)
    slug = slug_match.group(1)
    # Replace opening <div with <a, add href
    new_head = head.replace("<div ", f'<a href="projects/{slug}.html" ', 1)
    return f'{new_head}{body}</a>'

# Strategy: find each <div class="project-card ...">...</div> block.
# Use a non-greedy match between <div class="project-card and </div> closing the card.
pattern = re.compile(
    r'(<div class="project-card[^"]*"(?:[^>]*?)>)(.*?)</div>\s*(?=\s*<div class="project-card|\s*</div>\s*</section>)',
    re.DOTALL
)

def replace_card(m):
    head = m.group(1)
    body = m.group(2)
    slug_match = re.search(r'src="images/([a-z0-9-]+)\.jpg"', body)
    if not slug_match:
        return m.group(0)
    slug = slug_match.group(1)
    new_head = head.replace("<div ", '<a ', 1).rstrip('>') + f' href="projects/{slug}.html">'
    return f'{new_head}{body}</a>'

src, n = pattern.subn(replace_card, src)
print(f"Converted {n} project cards to anchor tags")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(src)

print(f"Main page updated. File size: {len(src)//1024} KB")
