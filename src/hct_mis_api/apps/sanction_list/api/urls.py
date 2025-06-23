from rest_framework.routers import DefaultRouter

from hct_mis_api.apps.sanction_list.api.views import SanctionListIndividualViewSet

app_name = "sanction-list"

router = DefaultRouter()
router.register(r"sanction-list", SanctionListIndividualViewSet, basename="sanction-list")

urlpatterns = [
    *router.urls,
]
