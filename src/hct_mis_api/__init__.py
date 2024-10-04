import importlib.metadata
import os

from django.conf import settings

import tomli


def get_full_version() -> str:
    try:
        # works in dist image
        version = importlib.metadata.version("hope")
        return version
    except importlib.metadata.PackageNotFoundError:
        # works in local and dev image
        with open(os.path.join(settings.PROJECT_ROOT, "../../pyproject.toml"), mode="rb") as fp:
            config = tomli.load(fp)
        return config["project"]["version"]
