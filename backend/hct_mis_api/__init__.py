import tomli


def get_full_version():
    with open("pyproject.toml", mode="rb") as fp:
        config = tomli.load(fp)
    return config["tool"]["poetry"]["version"]
