from django.urls import include, path

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.program.api.urls import program_base_router
from hope.apps.registration_data.api.views import RegistrationDataImportViewSet
from hope.apps.registration_data.api.views_import_data import (
    ImportDataViewSet,
    KoboImportDataViewSet,
)
from hope.apps.registration_data.api.views_upload import (
    ImportDataUploadViewSet,
    KoboImportDataUploadViewSet,
)

app_name = "registration_data"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "registration-data-imports",
    RegistrationDataImportViewSet,
    basename="registration-data-imports",
)

# Upload actions are program-specific (need program context for celery tasks)
program_nested_router.register(
    "import-data-upload",
    ImportDataUploadViewSet,
    basename="import-data-upload",
)
program_nested_router.register(
    "kobo-import-data-upload",
    KoboImportDataUploadViewSet,
    basename="kobo-import-data-upload",
)

# Retrieve actions are business area level (no program needed for viewing)
business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "import-data",
    ImportDataViewSet,
    basename="import-data",
)
business_area_nested_router.register(
    "kobo-import-data",
    KoboImportDataViewSet,
    basename="kobo-import-data",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
