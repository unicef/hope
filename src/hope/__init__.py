from importlib.metadata import version, PackageNotFoundError


def get_full_version() -> str:
    try:
        return version("hope")
    except PackageNotFoundError:
        return "1.0.0"
