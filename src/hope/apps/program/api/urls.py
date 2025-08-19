from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.program.api.views import (
    BeneficiaryGroupViewSet,
    ProgramCycleViewSet,
    ProgramViewSet,
)

app_name = "program"


class ProgramBaseNestedRouter:
    def __init__(self) -> None:
        self.business_area_nested_router = get_business_area_nested_router()
        self.business_area_nested_router.register(r"programs", ProgramViewSet, basename="programs")

    @property
    def program_nested_router(self) -> NestedSimpleRouter:
        return NestedSimpleRouter(self.business_area_nested_router, r"programs", lookup="program")


program_base_router = ProgramBaseNestedRouter()

router = SimpleRouter()
router.register(r"beneficiary-groups", BeneficiaryGroupViewSet, basename="beneficiary-groups")

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(r"cycles", ProgramCycleViewSet, basename="cycles")

urlpatterns = [
    path("", include(program_base_router.business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
    path("", include(router.urls)),
]
