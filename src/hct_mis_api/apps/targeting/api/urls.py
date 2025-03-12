from django.urls import include, path

from hct_mis_api.apps.program.api.urls import program_base_router
from hct_mis_api.apps.targeting.api.views import TargetPopulationViewSet

app_name = "targeting"

program_nested_router = program_base_router.program_nested_router

program_nested_router.register(
    r"target-populations",
    TargetPopulationViewSet,
    basename="target-populations",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
