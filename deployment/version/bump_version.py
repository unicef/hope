import json
import os
import re
import subprocess
import sys
from datetime import date


def bump_version():
    hotfix = "hotfix" in sys.argv
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/../../frontend/package.json") as f:
        json_dict = json.load(f)
    frontend_version = json_dict["version"]
    if hotfix:
        new_version = get_hotfix_new_version(frontend_version)
    else:
        new_version = get_normal_new_version(frontend_version)
    subprocess.run([f"{dir_path}/bump_version.sh", new_version], cwd=f"{dir_path}/../../")


def get_hotfix_new_version(version_string):
    version_regex = "(\d+).(\d+).(\d+)-hotfix-(\d+)"
    match = re.match(version_regex, version_string)
    if not match:
        return f"{version_string}-hotfix-1"
    (year, month, minor, hotfix_version) = match.groups()
    current_hotfix = str(int(hotfix_version) + 1)
    return f"{year}.{month}.{minor}-hotfix-{current_hotfix}"


def get_normal_new_version(version_string):
    version_regex = "(\d+).(\d+).(\d+).*"
    (old_year, old_month, old_minor) = re.match(version_regex, version_string).groups()
    current_year = str(date.today().year)
    current_month = str(date.today().month)
    if old_year == current_year and current_month == old_month:
        current_minor = str(int(old_minor) + 1)
    else:
        current_minor = 1
    return f"{current_year}.{current_month}.{current_minor}"


bump_version()
