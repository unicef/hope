#!/usr/bin/env python3
from tomlkit.api import loads
import json

with open("backend/pyproject.toml", "r") as f:
    toml_dict = loads(f.read())
with open("frontend/package.json", "r") as f:
    json_dict = json.load(f)
backend_version = toml_dict["tool"]["poetry"]["version"]
frontend_version = json_dict["version"]
print(f"Backend Version: {backend_version}")
print(f"Frontend Version: {frontend_version}")
print("Provide new version:")
new_version = str(input())
toml_dict["tool"]["poetry"]["version"] = new_version
json_dict["version"] = new_version

with open("backend/pyproject.toml", "w") as f:
    f.write(toml_dict.as_string())
with open("frontend/package.json", "w") as f:
    json.dump(json_dict, f, indent=2)
    f.write("\n")
