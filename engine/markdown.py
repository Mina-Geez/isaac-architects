import re
from html import escape

_EM = re.compile(r"(?<!\w)[*_]([^*_]+)[*_](?!\w)")


def render_paragraphs(text: str) -> str:
    """Blank-line separated paragraphs; *word*/_word_ -> <em>. Escapes HTML."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    out = []
    for p in paras:
        safe = escape(p)
        safe = _EM.sub(r"<em>\1</em>", safe)
        out.append(f"<p>{safe}</p>")
    return "\n".join(out)
