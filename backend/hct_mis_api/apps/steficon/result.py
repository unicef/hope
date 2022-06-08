class Result:
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return "<steficon.result.Result object at {}>".format(id(self))

    def __str__(self):
        return "Result: {}".format(self.value)


class Score(Result):
    def __init__(self):
        super().__init__()
        self.extra = {}

    def __repr__(self):
        return "<steficon.result.Score object at {}>".format(id(self))

    def __str__(self):
        return "Score: {}".format(self.value)
