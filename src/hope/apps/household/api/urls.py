from django.urls import include, path
from rest_framework_nested.routers import NestedDefaultRouter

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.household.api.views import (
    HouseholdGlobalViewSet,
    HouseholdViewSet,
    IndividualGlobalViewSet,
    IndividualViewSet,
)
from hope.apps.payment.api.views import AccountAttachmentViewSet, AccountViewSet
from hope.apps.program.api.urls import program_base_router

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

individuals_nested_router = NestedDefaultRouter(program_nested_router, "individuals", lookup="individual")
individuals_nested_router.register("accounts", AccountViewSet, basename="accounts")

accounts_nested_router = NestedDefaultRouter(individuals_nested_router, "accounts", lookup="account")
accounts_nested_router.register("attachments", AccountAttachmentViewSet, basename="account-attachments")


urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
    path("", include(individuals_nested_router.urls)),
    path("", include(accounts_nested_router.urls)),
]
