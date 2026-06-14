import jinja2

from engine.paths import TEMPLATES


def make_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES)),
        autoescape=jinja2.select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True)
    return env


def gallery_shapes(n):
    """Editorial mosaic rhythm: full-width opener, alternating asymmetric pairs,
    square pairs, periodic full-width bands. Every row fills cleanly (3-8 images)."""
    recipes = [["g-full"], ["g-major", "g-minor"], ["g-square", "g-square"], ["g-minor", "g-major"]]
    shapes, i, r = [], 0, 0
    while i < n:
        recipe = recipes[r % len(recipes)]
        if len(recipe) <= n - i:
            shapes += recipe
            i += len(recipe)
        else:
            shapes.append("g-full")
            i += 1
        r += 1
    return shapes
