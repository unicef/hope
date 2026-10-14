from django.conf import settings


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


def frontend_url(path: str = "") -> str:
    """Join ``path`` onto the absolute address of the HOPE frontend."""
    protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
    return build_url(f"{protocol}://{settings.FRONTEND_HOST}", path)
