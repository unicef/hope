from django.urls import include, path

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.grievance.api.views import (
    GrievanceTicketGlobalViewSet,
    GrievanceTicketViewSet,
)
from hope.apps.program.api.urls import program_base_router

app_name = "grievance"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "grievance-tickets",
    GrievanceTicketViewSet,
    basename="grievance-tickets",
)
business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "grievance-tickets",
    GrievanceTicketGlobalViewSet,
    basename="grievance-tickets-global",
)


urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
