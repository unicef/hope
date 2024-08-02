from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.registration_data.api.views import RegistrationDataImportViewSet

app_name = "registration_data"

router = SimpleRouter()
router.register(
    "registration-data-imports",
    RegistrationDataImportViewSet,
    basename="registration-data-imports",
)

urlpatterns = [
    path("", include(router.urls)),
]
