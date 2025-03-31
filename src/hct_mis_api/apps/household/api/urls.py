from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.household.api.views import (
    HouseholdGlobalViewSet,
    HouseholdViewSet,
    IndividualViewSet,
    IndividualGlobalViewSet,
)
from hct_mis_api.apps.program.api.urls import program_base_router

app_name = "household"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "households",
    HouseholdViewSet,
    basename="households",
)
program_nested_router.register(
    "individuals",
    IndividualViewSet,
    basename="individuals",
)
business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register("households", HouseholdGlobalViewSet, basename="households-global")
business_area_nested_router.register("individuals", IndividualGlobalViewSet, basename="individuals-global")


urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
