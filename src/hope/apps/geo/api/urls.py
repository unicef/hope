from django.urls import include, path

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.geo.api.views import AreaViewSet

app_name = "geo"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "geo/areas",
    AreaViewSet,
    basename="areas",
)

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
]
