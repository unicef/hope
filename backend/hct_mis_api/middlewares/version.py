from django.conf import settings


class VersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Hope-Backend-Version"] = settings.VERSION
        return response
