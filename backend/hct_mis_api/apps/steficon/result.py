class Result:
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return "<steficon.result.Result object at %s>" % id(self)

    def __str__(self):
        return "Result: %s" % self.value


class Score(Result):
    pass
