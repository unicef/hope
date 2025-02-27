from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.program.api.views import (
    BeneficiaryGroupViewSet,
    ProgramCycleViewSet,
    ProgramViewSet,
)

app_name = "program"


def get_program_nested_router() -> NestedSimpleRouter:
    return NestedSimpleRouter(business_area_nested_router, r"programs", lookup="program")


router = SimpleRouter()
router.register(r"beneficiary-groups", BeneficiaryGroupViewSet, basename="beneficiary-groups")

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(r"programs", ProgramViewSet, basename="programs")

program_nested_router = NestedSimpleRouter(business_area_nested_router, r"programs", lookup="program")
program_nested_router.register(r"cycles", ProgramCycleViewSet, basename="cycles")

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
    path("", include(router.urls)),
]
