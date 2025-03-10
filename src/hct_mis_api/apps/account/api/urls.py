from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.account.api.views import UserViewSet

app_name = "account"

router = SimpleRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
