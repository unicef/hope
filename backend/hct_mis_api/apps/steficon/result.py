class Result:
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return f"<steficon.result.Result object at {id(self)}>"

    def __str__(self):
        return f"Result: {self.value}"


class Score(Result):
    def __init__(self):
        super().__init__()
        self.extra = {}

    def __repr__(self):
        return f"<steficon.result.Score object at {id(self)}>"

    def __str__(self):
        return f"Score: {self.value}"
