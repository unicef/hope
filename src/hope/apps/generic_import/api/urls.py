from django.urls import include, path

from hope.apps.generic_import.api.views import GenericImportUploadViewSet
from hope.apps.program.api.urls import program_base_router

app_name = "generic_import"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "generic-import-upload",
    GenericImportUploadViewSet,
    basename="generic-import-upload",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
