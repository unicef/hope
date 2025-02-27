from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hct_mis_api.apps.core.api.views import BusinessAreaViewSet

app_name = "core"


router = routers.SimpleRouter()


router.register(r"business_areas", BusinessAreaViewSet, basename="business_area")


urlpatterns = router.urls


def get_business_area_nested_router() -> NestedSimpleRouter:
    return NestedSimpleRouter(router, r"business_areas", lookup="business_area")
