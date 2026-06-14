import tomllib

FENCE = "+++"


def parse(raw: str):
    """Split a '+++ TOML +++ body' document into (dict, body_str)."""
    s = raw.lstrip("﻿").lstrip()
    if not s.startswith(FENCE):
        raise ValueError("missing opening +++ frontmatter fence")
    rest = s[len(FENCE):]
    end = rest.find("\n" + FENCE)
    if end == -1:
        raise ValueError("missing closing +++ frontmatter fence")
    toml_src = rest[:end]
    body = rest[end + len("\n" + FENCE):].lstrip("\n")
    meta = tomllib.loads(toml_src)
    return meta, body
