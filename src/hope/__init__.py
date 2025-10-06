from importlib.metadata import PackageNotFoundError, version


def get_full_version() -> str:
    try:
        return version("hope")
    except PackageNotFoundError:
        return "1.0.0"
