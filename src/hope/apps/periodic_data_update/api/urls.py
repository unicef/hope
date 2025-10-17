from django.urls import include, path

from hope.apps.periodic_data_update.api.views import (
    PDUOnlineEditViewSet,
    PDUXlsxTemplateViewSet,
    PDUXlsxUploadViewSet,
    PeriodicFieldViewSet,
)
from hope.apps.program.api.urls import program_base_router

app_name = "periodic_data_update"

program_nested_router = program_base_router.program_nested_router

program_nested_router.register(
    "periodic-data-update-templates",
    PDUXlsxTemplateViewSet,
    basename="periodic-data-update-templates",
)
program_nested_router.register(
    "periodic-data-update-uploads",
    PDUXlsxUploadViewSet,
    basename="periodic-data-update-uploads",
)
program_nested_router.register(
    "periodic-data-update-online-edits",
    PDUOnlineEditViewSet,
    basename="periodic-data-update-online-edits",
)
program_nested_router.register(
    "periodic-fields",
    PeriodicFieldViewSet,
    basename="periodic-fields",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
