from django.urls import include, path

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.sanction_list.api.views import SanctionListIndividualViewSet

app_name = "sanction-list"


business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(r"sanction-list", SanctionListIndividualViewSet, basename="sanction-list")


urlpatterns = [
    path("", include(business_area_nested_router.urls)),
]
