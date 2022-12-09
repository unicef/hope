from typing import Any


class RuleError(Exception):
    def __init__(self, rule: Any, error_class: Any, detail: Any, line_number: int, traceback: Any = None) -> None:
        self.rule = rule
        self.error_class = error_class
        self.detail = detail
        self.lineno = line_number
        self.traceback = traceback

    def __str__(self) -> str:
        return f"{self.error_class}: {self.detail} at {self.lineno}"
