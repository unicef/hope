class RuleError(Exception):
    def __init__(
        self,
        rule: object,
        error_class: object,
        detail: object,
        line_number: int | None,
        traceback: object | None = None,
    ) -> None:
        self.rule = rule
        self.error_class = error_class
        self.detail = detail
        self.lineno = line_number
        self.traceback = traceback

    def __str__(self) -> str:
        return f"{self.error_class}: {self.detail} at {self.lineno}"
