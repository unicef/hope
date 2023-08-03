from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from hct_mis_api.apps.core.models import MigrationStatus


class DisableTrafficDuringMigrationsMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if MigrationStatus.objects.filter(is_running=True).exists() and not request.path.startswith(
            f"/api/{settings.ADMIN_PANEL_URL}"
        ):
            return JsonResponse(
                {"message": "Migrations are running, please try again later"},
                status=403,
            )
        return self.get_response(request)
