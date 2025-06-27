from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse


class DisableTrafficDuringMigrationsMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        allowed_paths_beginnings = [
            f"/api/{settings.ADMIN_PANEL_URL}",
            "/_health",
            "/api/_health",
        ]
        if not any(request.path.startswith(path) for path in allowed_paths_beginnings):
            return JsonResponse(
                {"message": "Migrations are running, please try again later"},
                status=403,
            )
        return self.get_response(request)
