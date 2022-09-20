from django.urls import include, path, re_path

from . import endpoints
from .router import APIRouter

app_name = "api"

router = APIRouter()

urlpatterns = [
    re_path(r"", include(router.urls)),
    path("rdi/<slug:business_area>/upload/", endpoints.UploadRDIView().as_view(), name="rdi-upload"),
    path("countries/", endpoints.CountryList().as_view(), name="country-list"),
    path("areas/", endpoints.AreaList().as_view(), name="area-list"),
    path("areatypes/", endpoints.AreaTypeList().as_view(), name="areatype-list"),
    path("lookups/document/", endpoints.DocumentType().as_view(), name="document-list"),
    path("lookups/country/", endpoints.Country().as_view(), name="country-list"),
    path("lookups/residencestatus/", endpoints.ResidenceStatus().as_view(), name="residencestatus-list"),
    path("lookups/maritalstatus/", endpoints.MaritalStatus().as_view(), name="maritalstatus-list"),
    path("lookups/observeddisability/", endpoints.ObservedDisability().as_view(), name="observeddisability-list"),
    path("lookups/relationship/", endpoints.Relationship().as_view(), name="relationship-list"),
    path("lookups/datacollectingpolicy/", endpoints.DataCollectingPolicy().as_view(), name="datacollectingpolicy-list"),
    path("lookups/role/", endpoints.Roles().as_view(), name="role-list"),
]
