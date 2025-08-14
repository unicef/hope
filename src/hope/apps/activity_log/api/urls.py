from django.urls import include, path

from hope.apps.activity_log.api.views import LogEntryViewSet
from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.program.api.urls import program_base_router

app_name = "activity_log"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "activity-logs",
    LogEntryViewSet,
    basename="activity-logs",
)

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "activity-logs",
    LogEntryViewSet,
    basename="activity-logs-per-program",
)

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
]
