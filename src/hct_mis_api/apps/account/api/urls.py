from django.urls import include, path

from hct_mis_api.apps.account.api.views import UserViewSet
from hct_mis_api.apps.core.api.urls import get_business_area_nested_router

app_name = "account"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
]
