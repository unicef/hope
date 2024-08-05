from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.geo.api.views import AreaViewSet

app_name = "geo"

router = SimpleRouter()
router.register(
    "areas",
    AreaViewSet,
    basename="areas",
)

urlpatterns = [
    path("", include(router.urls)),
]
