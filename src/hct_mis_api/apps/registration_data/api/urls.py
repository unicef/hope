from django.urls import include, path

from hct_mis_api.apps.program.api.urls import program_base_router
from hct_mis_api.apps.registration_data.api.views import RegistrationDataImportViewSet

app_name = "registration_data"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "registration-data-imports",
    RegistrationDataImportViewSet,
    basename="registration-data-imports",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
