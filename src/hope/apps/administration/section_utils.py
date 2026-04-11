"""Helpers for the HOPE smart-index grouping.

Ported from ``smart_admin.utils`` when the ``django-smart-admin`` dependency
was dropped. Only the bits needed for section matching and the
``smart`` cookie parsing are kept.
"""

from fnmatch import fnmatchcase
import re
from typing import Any


def as_bool(value: Any) -> bool:
    return value not in ("", "0", "None", 0, None, "on")


class MatchString(str):
    def __repr__(self) -> str:
        return f"m[{self}]"


class RegexString(str):
    def __init__(self, pattern: str, options: int = 0) -> None:
        self._rex = re.compile(pattern, options)

    def __repr__(self) -> str:
        return f"r[{self._rex.pattern}]"


class SmartList(list):
    def __contains__(self, target: Any) -> bool:
        t = str(target)
        for entry in self:
            if isinstance(entry, MatchString):
                if fnmatchcase(t, entry):
                    return True
            elif isinstance(entry, RegexString):
                m = entry._rex.match(t)
                if m and m.group():
                    return True
            elif entry == target:
                return True
        return False
