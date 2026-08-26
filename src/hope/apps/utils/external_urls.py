def normalize_base_url(base_url: str | None) -> str:
    """Return ``base_url`` without surrounding whitespace or trailing slashes."""
    return (base_url or "").strip().rstrip("/")


def build_url(base_url: str | None, path: str = "") -> str:
    """Join ``base_url`` and ``path`` with exactly one slash between them.

    ``path`` keeps its own trailing slash and query string; only the separator is normalized.
    """
    base = normalize_base_url(base_url)
    path = path.lstrip("/")
    if not path:
        return base
    return f"{base}/{path}"
