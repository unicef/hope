from django.urls import include, path

from hct_mis_api.apps.program.api.urls import get_program_nested_router
from hct_mis_api.apps.targeting.api.views import TargetPopulationViewSet

app_name = "targeting"

program_nested_router = get_program_nested_router()

program_nested_router.register(
    r"target-populations",
    TargetPopulationViewSet,
    basename="target-populations",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
