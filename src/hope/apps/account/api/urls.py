from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hope.apps.account.api.views import GroupViewSet, UserViewSet
from hope.apps.core.api.urls import get_business_area_nested_router

app_name = "account"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register("users", UserViewSet, basename="users")

router = DefaultRouter()
router.register("groups", GroupViewSet, basename="groups")

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(router.urls)),
]
