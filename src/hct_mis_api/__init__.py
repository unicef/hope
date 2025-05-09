import importlib.metadata


def get_full_version() -> str:
    return importlib.metadata.version("hope")
