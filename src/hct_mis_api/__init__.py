import importlib.metadata


def get_full_version() -> str:
    version = importlib.metadata.version("hope")
    return version