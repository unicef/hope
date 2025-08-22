from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from hope.api import endpoints
from hope.api.endpoints.base import ConstanceSettingsAPIView
from hope.api.endpoints.program.views import ProgramGlobalListView
from hope.apps.core.api.views import ChoicesViewSet
from hope.apps.steficon.views import RuleEngineViewSet
from hope.contrib.aurora.views import (
    OrganizationListView,
    ProjectListView,
    RegistrationListView,
)

app_name = "api"

router = DefaultRouter()
router.register(r"choices", ChoicesViewSet, basename="choices")


urlpatterns = [
    re_path("^$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        "^swagger/$",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    re_path("^redoc/$", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
    path("", include("hope.apps.accountability.api.urls", namespace="accountability")),
    path("", include("hope.apps.activity_log.api.urls", namespace="activity-logs")),
    path("", include("hope.apps.core.api.urls", namespace="core")),
    path("", include("hope.apps.payment.api.urls", namespace="payments")),
    path("", include("hope.apps.program.api.urls", namespace="programs")),
    path("", include("hope.apps.targeting.api.urls", namespace="targeting")),
    path(
        "",
        include("hope.apps.registration_data.api.urls", namespace="registration-data"),
    ),
    path("", include("hope.apps.household.api.urls", namespace="households")),
    path("", include("hope.apps.grievance.api.urls", namespace="grievance-tickets")),
    path(
        "",
        include("hope.apps.periodic_data_update.api.urls", namespace="periodic-data-update"),
    ),
    path(
        "",
        include("hope.apps.geo.api.urls", namespace="geo"),
    ),
    path("", include("hope.apps.account.api.urls", namespace="accounts")),
    path("", include("hope.apps.sanction_list.api.urls", namespace="sanction-list")),
    # choices
    path("", include(router.urls)),
    # old urls
    path("areas/", endpoints.lookups.AreaList().as_view(), name="area-list"),
    path("areatypes/", endpoints.lookups.AreaTypeList().as_view(), name="areatype-list"),
    path("constance/", ConstanceSettingsAPIView().as_view(), name="constance-list"),
    path("engine-rules/", RuleEngineViewSet().as_view(), name="engine-rules-list"),
    path(
        "lookups/document/",
        endpoints.lookups.DocumentType().as_view(),
        name="document-list",
    ),
    path(
        "lookups/country/",
        endpoints.lookups.CountryAPIView().as_view(),
        name="country-list",
    ),
    path(
        "lookups/financial-institution/",
        endpoints.lookups.FinancialInstitutionAPIView().as_view(),
        name="financial-institution-list",
    ),
    path(
        "lookups/residencestatus/",
        endpoints.lookups.ResidenceStatus().as_view(),
        name="residencestatus-list",
    ),
    path(
        "lookups/maritalstatus/",
        endpoints.lookups.MaritalStatus().as_view(),
        name="maritalstatus-list",
    ),
    path(
        "lookups/observeddisability/",
        endpoints.lookups.ObservedDisability().as_view(),
        name="observeddisability-list",
    ),
    path(
        "lookups/relationship/",
        endpoints.lookups.Relationship().as_view(),
        name="relationship-list",
    ),
    path("lookups/role/", endpoints.lookups.Roles().as_view(), name="role-list"),
    path("lookups/sex/", endpoints.lookups.Sex().as_view(), name="sex-list"),
    path(
        "lookups/program-statuses/",
        endpoints.lookups.ProgramStatuses().as_view(),
        name="program-statuses-list",
    ),
    path("programs/", ProgramGlobalListView.as_view(), name="program-global-list"),
    path("dashboard/", include("hope.apps.dashboard.urls")),
    path(
        "systems/aurora/",
        include(
            [
                path("offices/", OrganizationListView.as_view(), name="organization-list"),
                path("projects/", ProjectListView.as_view(), name="project-list"),
                path(
                    "registrations/",
                    RegistrationListView.as_view(),
                    name="registration-list",
                ),
            ]
        ),
    ),
    path(
        "<slug:business_area>/",
        include(
            [
                path(
                    "program/",
                    endpoints.rdi.ProgramViewSet.as_view({"get": "list"}),
                    name="program-list",
                ),
                path(
                    "program/create/",
                    endpoints.rdi.ProgramViewSet.as_view({"post": "create"}),
                    name="program-create",
                ),
                path(
                    "rdi/create/",
                    endpoints.rdi.CreateRDIView().as_view(),
                    name="rdi-create",
                ),
                path(
                    "rdi/upload/",
                    endpoints.rdi.UploadRDIView().as_view(),
                    name="rdi-upload",
                ),
                path(
                    "rdi/<uuid:rdi>/completed/",
                    endpoints.rdi.CompleteRDIView().as_view(),
                    name="rdi-complete",
                ),
                path(
                    "rdi/<uuid:rdi>/delegate/people/",
                    endpoints.rdi.DelegatePeopleRDIView().as_view(),
                    name="rdi-delegate-people",
                ),
                path(
                    "rdi/<uuid:rdi>/push/",
                    endpoints.rdi.PushToRDIView().as_view(),
                    name="rdi-push",
                ),
                path(
                    "rdi/<uuid:rdi>/push/people/",
                    endpoints.rdi.PushPeopleToRDIView().as_view(),
                    name="rdi-push-people",
                ),
                path(
                    "rdi/<uuid:rdi>/push/lax/",
                    endpoints.rdi.PushLaxToRDIView().as_view(),
                    name="rdi-push-lax",
                ),
                path(
                    "rdi/<uuid:rdi>/push/lax/individuals",
                    endpoints.rdi.CreateLaxIndividuals().as_view(),
                    name="rdi-push-lax-individuals",
                ),
                path(
                    "rdi/<uuid:rdi>/push/lax/households",
                    endpoints.rdi.CreateLaxHouseholds().as_view(),
                    name="rdi-push-lax-households",
                ),
            ]
        ),
    ),
]
