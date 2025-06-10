import importlib.metadata


def get_full_version() -> str:
    try:
        return importlib.metadata.version("hope")
    except Exception:
        return "1.0.0"
