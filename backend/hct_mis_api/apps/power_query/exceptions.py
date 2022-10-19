class QueryRunError(Exception):
    def __init__(self, exception, sentry_error_id, *args, **kwargs):
        self.exception = exception
        self.sentry_error_id = sentry_error_id

    def __str__(self):
        return str(self.exception)
