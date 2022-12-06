class Result:
    def __init__(self) -> None:
        self.value = 0

    def __repr__(self) -> str:
        return "<steficon.result.Result object at {}>".format(id(self))

    def __str__(self) -> str:
        return "Result: {}".format(self.value)


class Score(Result):
    def __init__(self) -> None:
        super().__init__()
        self.extra = {}

    def __repr__(self) -> str:
        return "<steficon.result.Score object at {}>".format(id(self))

    def __str__(self) -> str:
        return "Score: {}".format(self.value)
