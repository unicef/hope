from django.urls import include, path, re_path

from . import endpoints
from .router import APIRouter

app_name = "api"

router = APIRouter()

urlpatterns = [
    re_path(r"(?P<version>(v1|v2|latest))/", include(router.urls)),
    path("rdi/<slug:business_area>/upload/", endpoints.UploadRDIView().as_view(), name="rdi-upload"),
    path("countries/", endpoints.CountryList().as_view(), name="country-list"),
    path("areas/", endpoints.AreaList().as_view(), name="area-list"),
    path("areatypes/", endpoints.AreaTypeList().as_view(), name="areatype-list"),
]
