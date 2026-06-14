import hashlib


def hashed_name(name: str, content: bytes) -> str:
    h = hashlib.sha256(content).hexdigest()[:10]
    stem, _, ext = name.rpartition(".")
    return f"{stem}.{h}.{ext}"
