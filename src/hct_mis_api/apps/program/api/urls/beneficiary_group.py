from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.program.api.views import BeneficiaryGroupViewSet

app_name = "program"
router = SimpleRouter()
router.register(r"beneficiary-groups", BeneficiaryGroupViewSet, basename="beneficiary-group")

urlpatterns = [
    path("", include(router.urls)),
]
