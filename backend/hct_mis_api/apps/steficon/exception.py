class RuleError(Exception):
    def __init__(self, rule, error_class, detail, line_number, traceback=None):
        self.rule = rule
        self.error_class = error_class
        self.detail = detail
        self.lineno = line_number
        self.traceback = traceback

    def __str__(self):
        return f"{self.error_class}: {self.detail}"
