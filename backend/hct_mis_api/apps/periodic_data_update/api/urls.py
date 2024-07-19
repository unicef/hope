from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.periodic_data_update.api.views import (
    PeriodicDataFieldViewSet,
    PeriodicDataUpdateTemplateViewSet,
    PeriodicDataUpdateUploadViewSet,
)

app_name = "periodic_data_update"

router = SimpleRouter()
router.register(
    "periodic-data-update-templates",
    PeriodicDataUpdateTemplateViewSet,
    basename="periodic-data-update-templates",
)
router.register(
    "periodic-data-update-uploads",
    PeriodicDataUpdateUploadViewSet,
    basename="periodic-data-update-uploads",
)
router.register(
    "periodic-data-fields",
    PeriodicDataFieldViewSet,
    basename="periodic-data-fields",
)

urlpatterns = [
    path("", include(router.urls)),
]
