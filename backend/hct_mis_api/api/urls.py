from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import endpoints
from .router import APIRouter

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
    path("<slug:business_area>/rdi/upload/", endpoints.UploadRDIView().as_view(), name="rdi-upload"),
    path("<slug:business_area>/rdi/create/", endpoints.CreateRDIView().as_view(), name="rdi-create"),
    path("<slug:business_area>/rdi/<uuid:rdi>/push/lax/", endpoints.PushLaxToRDIView().as_view(), name="rdi-push-lax"),
    path("<slug:business_area>/rdi/<uuid:rdi>/push/", endpoints.PushToRDIView().as_view(), name="rdi-push"),
    path("<slug:business_area>/rdi/<uuid:rdi>/completed/", endpoints.CompleteRDIView().as_view(), name="rdi-complete"),
    path(
        "<slug:business_area>/program/create/",
        endpoints.ProgramViewSet.as_view({"post": "create"}),
        name="program-create",
    ),
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
    path("lookups/sex/", endpoints.Sex().as_view(), name="sex-list"),
]
