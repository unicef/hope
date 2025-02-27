from django.urls import include, path

from hct_mis_api.apps.program.api.urls import get_program_nested_router
from hct_mis_api.apps.registration_data.api.views import (
    RegistrationDataImportViewSet,
    WebhookDeduplicationView,
)

app_name = "registration_data"

program_nested_router = get_program_nested_router()
program_nested_router.register(
    "registration-data-imports",
    RegistrationDataImportViewSet,
    basename="registration-data-imports",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("webhookdeduplication/", WebhookDeduplicationView.as_view(), name="webhook_deduplication"),
]
