#!/usr/bin/env python3
import json

with open("frontend/package.json", "r") as f:
    json_dict = json.load(f)
frontend_version = json_dict["version"]
print(frontend_version)

