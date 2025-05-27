from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.grievance.api.views import (GrievanceTicketGlobalViewSet,
                                                  GrievanceTicketViewSet)
from hct_mis_api.apps.program.api.urls import program_base_router

app_name = "grievance"

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "grievance-tickets",
    GrievanceTicketViewSet,
    basename="grievance-tickets",
)
business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "grievance-tickets", GrievanceTicketGlobalViewSet, basename="grievance-tickets-global"
)


urlpatterns = [
    path("", include(program_nested_router.urls)),
    path("", include(business_area_nested_router.urls)),
]
