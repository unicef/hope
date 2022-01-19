class Result:
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return "<steficon.result.Result object at %s>" % id(self)

    def __str__(self):
        return "Result: %s" % self.value


class Score(Result):
    def __init__(self):
        super(Score, self).__init__()
        self.extra = {}

    def __repr__(self):
        return "<steficon.result.Score object at %s>" % id(self)

    def __str__(self):
        return "Score: %s" % self.value
