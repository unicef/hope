from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.geo.api.views import AreaViewSet

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
