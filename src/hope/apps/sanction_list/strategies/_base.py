class BaseSanctionList:
    def __init__(self, context: "SanctionList") -> None:
        self.context = context

    def refresh(self) -> None:
        raise NotImplementedError()
