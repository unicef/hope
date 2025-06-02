import importlib.metadata


def get_full_version() -> str:
    try:
        version = importlib.metadata.version("hope")
    except importlib.metadata.PackageNotFoundError:
        version = "3.2.0"  # Fallback for development environments
    return version
