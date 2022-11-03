from typing import Dict
import tomli


def get_full_version() -> str:
    with open("pyproject.toml", mode="rb") as fp:
        config: Dict = tomli.load(fp)
    poetry_config: Dict[str, str] = config["tool"]["poetry"]
    return poetry_config["version"]
