from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.program.api.views import ProgramCycleViewSet

app_name = "program"
router = SimpleRouter()
router.register(r"cycles", ProgramCycleViewSet, basename="cycles")

urlpatterns = [
    path("", include(router.urls)),
]
