import pathlib
import tomllib


def load_settings(path: pathlib.Path) -> dict:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if "canonical_base" not in data:
        raise ValueError("settings.toml: canonical_base required")
    data["canonical_base"] = data["canonical_base"].rstrip("/")
    return data
