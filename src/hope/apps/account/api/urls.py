from django.urls import include, path

from hope.apps.account.api.views import UserViewSet
from hope.apps.core.api.urls import get_business_area_nested_router

app_name = "account"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
]
