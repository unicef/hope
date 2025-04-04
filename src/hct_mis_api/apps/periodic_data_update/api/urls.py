from django.urls import include, path

from hct_mis_api.apps.periodic_data_update.api.views import (
    PeriodicDataUpdateTemplateViewSet,
    PeriodicDataUpdateUploadViewSet,
    PeriodicFieldViewSet,
)
from hct_mis_api.apps.program.api.urls import program_base_router

app_name = "periodic_data_update"

program_nested_router = program_base_router.program_nested_router

program_nested_router.register(
    "periodic-data-update-templates",
    PeriodicDataUpdateTemplateViewSet,
    basename="periodic-data-update-templates",
)
program_nested_router.register(
    "periodic-data-update-uploads",
    PeriodicDataUpdateUploadViewSet,
    basename="periodic-data-update-uploads",
)
program_nested_router.register(
    "periodic-fields",
    PeriodicFieldViewSet,
    basename="periodic-fields",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
