import sys

from sentry_sdk import configure_scope


class SentryScopeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__()

    # Note: must be listed AFTER AuthenticationMiddleware
    def __call__(self, request):
        sys.stderr.isatty = lambda: False
        with configure_scope() as scope:
            # TODO: add business area
            scope.set_tag("username", request.user.username)
            response = self.get_response(request)
        return response
