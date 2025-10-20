from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hope.apps.core.api.views import BusinessAreaViewSet

app_name = "core"


business_area_base_router = routers.SimpleRouter()


business_area_base_router.register(r"business-areas", BusinessAreaViewSet, basename="business-areas")


urlpatterns = business_area_base_router.urls


def get_business_area_nested_router() -> NestedSimpleRouter:
    return NestedSimpleRouter(business_area_base_router, r"business-areas", lookup="business_area")
