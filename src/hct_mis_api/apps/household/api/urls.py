from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.household.api.views import (
    HouseholdGlobalViewSet,
    HouseholdViewSet,
)
from hct_mis_api.apps.program.api.urls import get_program_nested_router

app_name = "payment"

program_nested_router = get_program_nested_router()
program_nested_router.register(
    "households",
    HouseholdViewSet,
    basename="households",
)
business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register("households", HouseholdGlobalViewSet, basename="households-global")

urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
