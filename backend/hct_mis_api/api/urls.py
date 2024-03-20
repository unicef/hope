from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from hct_mis_api.api import endpoints
from hct_mis_api.api.endpoints.base import ConstanceSettingsAPIView
from hct_mis_api.api.router import APIRouter

app_name = "api"

schema_view = get_schema_view(
    openapi.Info(
        title="Hope API documentation",
        default_version="v1",
        description="Hope API description",
        # terms_of_service="",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

router = APIRouter()

urlpatterns = [
    path(r"(<str:format>\.json|\.yaml)", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(r"", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("<slug:business_area>/rdi/upload/", endpoints.rdi.UploadRDIView().as_view(), name="rdi-upload"),
    path(
        "<slug:business_area>/rdi/upload/people/",
        endpoints.rdi.UploadPeopleRDIView().as_view(),
        name="rdi-upload-people",
    ),
    path("<slug:business_area>/rdi/create/", endpoints.rdi.CreateRDIView().as_view(), name="rdi-create"),
    path(
        "<slug:business_area>/rdi/<uuid:rdi>/push/people/",
        endpoints.rdi.PushPeopleToRDIView().as_view(),
        name="rdi-push-people",
    ),
    path(
        "<slug:business_area>/rdi/<uuid:rdi>/push/lax/", endpoints.rdi.PushLaxToRDIView().as_view(), name="rdi-push-lax"
    ),
    path("<slug:business_area>/rdi/<uuid:rdi>/push/", endpoints.rdi.PushToRDIView().as_view(), name="rdi-push"),
    path(
        "<slug:business_area>/rdi/<uuid:rdi>/delegate/people/",
        endpoints.rdi.DelegatePeopleRDIView().as_view(),
        name="rdi-delegate-people",
    ),
    path(
        "<slug:business_area>/rdi/<uuid:rdi>/completed/", endpoints.rdi.CompleteRDIView().as_view(), name="rdi-complete"
    ),
    path(
        "<slug:business_area>/program/",
        endpoints.rdi.ProgramViewSet.as_view({"get": "list"}),
        name="program-list",
    ),
    path(
        "<slug:business_area>/program/create/",
        endpoints.rdi.ProgramViewSet.as_view({"post": "create"}),
        name="program-create",
    ),
    path("areas/", endpoints.lookups.AreaList().as_view(), name="area-list"),
    path("areatypes/", endpoints.lookups.AreaTypeList().as_view(), name="areatype-list"),
    path("constance/", ConstanceSettingsAPIView().as_view(), name="constance-list"),
    path("lookups/document/", endpoints.lookups.DocumentType().as_view(), name="document-list"),
    path("lookups/country/", endpoints.lookups.Country().as_view(), name="country-list"),
    path("lookups/residencestatus/", endpoints.lookups.ResidenceStatus().as_view(), name="residencestatus-list"),
    path("lookups/maritalstatus/", endpoints.lookups.MaritalStatus().as_view(), name="maritalstatus-list"),
    path(
        "lookups/observeddisability/", endpoints.lookups.ObservedDisability().as_view(), name="observeddisability-list"
    ),
    path("lookups/relationship/", endpoints.lookups.Relationship().as_view(), name="relationship-list"),
    path(
        "lookups/datacollectingpolicy/",
        endpoints.lookups.DataCollectingPolicy().as_view(),
        name="datacollectingpolicy-list",
    ),
    path("lookups/role/", endpoints.lookups.Roles().as_view(), name="role-list"),
    path("lookups/sex/", endpoints.lookups.Sex().as_view(), name="sex-list"),
]
