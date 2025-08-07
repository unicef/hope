class Result:
    def __init__(self) -> None:
        self.value = 0

    def __repr__(self) -> str:
        return f"<steficon.result.Result object at {id(self)}>"

    def __str__(self) -> str:
        return f"Result: {self.value}"


class Score(Result):
    def __init__(self) -> None:
        super().__init__()
        self.extra: dict = {}

    def __repr__(self) -> str:
        return f"<steficon.result.Score object at {id(self)}>"

    def __str__(self) -> str:
        return f"Score: {self.value}"
