from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hope.apps.core.api.views import BusinessAreaViewSet, DataCollectingTypeViewSet

app_name = "core"


business_area_base_router = routers.SimpleRouter()


business_area_base_router.register(r"business-areas", BusinessAreaViewSet, basename="business-areas")


def get_business_area_nested_router() -> NestedSimpleRouter:
    return NestedSimpleRouter(business_area_base_router, r"business-areas", lookup="business_area")


business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    r"data-collecting-types",
    DataCollectingTypeViewSet,
    basename="data-collecting-types",
)


urlpatterns = [
    path("", include(business_area_base_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
