from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.targeting.api.views import TargetPopulationViewSet

app_name = "targeting"

router = SimpleRouter()
router.register(
    "target-populations",
    TargetPopulationViewSet,
    basename="target-populations",
)

urlpatterns = [
    path("", include(router.urls)),
]
