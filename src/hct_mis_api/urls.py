from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt

import adminactions.actions as actions
from graphene_file_upload.django import FileUploadGraphQLView

import hct_mis_api.apps.account.views
import hct_mis_api.apps.accountability.views
import hct_mis_api.apps.household.views
import hct_mis_api.apps.payment.views
import hct_mis_api.apps.registration_data.views
import hct_mis_api.apps.sanction_list.views
import hct_mis_api.apps.targeting.views
from hct_mis_api.apps.core.rest_api import all_fields_attributes
from hct_mis_api.apps.core.views import (
    UploadFile,
    homepage,
    hope_redirect,
    logout_view,
    schema,
    trigger_error,
)
from hct_mis_api.apps.utils.cypress import get_cypress_xlsx_file, handle_cypress_command
from hct_mis_api.apps.web.views import react_main

# register all adminactions
actions.add_to_site(site, exclude=["export_delete_tree"])

api_patterns = [
    path("rest/", include("hct_mis_api.api.urls", namespace="api")),
    path("", include("social_django.urls", namespace="social")),
    path("fields_attributes/", all_fields_attributes, name="fields_attributes"),
    path("_health", homepage),
    path("explorer/", include("explorer.urls")),
    path("hope-redirect", hope_redirect),
    path("graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path("graphql/schema.graphql", schema),
    path("logout", logout_view, name="logout"),
    path("sentry-debug/", trigger_error),
    path(
        "program/<str:program_id>/download-template",
        hct_mis_api.apps.registration_data.views.download_template,
    ),
    path(
        "download-exported-users/<str:business_area_slug>",
        hct_mis_api.apps.account.views.download_exported_users,
    ),
    path(
        "download-payment-verification-plan/<str:verification_id>",
        hct_mis_api.apps.payment.views.download_payment_verification_plan,
        name="download-payment-verification-plan",
    ),
    path(
        "download-payment-plan-payment-list/<str:payment_plan_id>",
        hct_mis_api.apps.payment.views.download_payment_plan_payment_list,
        name="download-payment-plan-payment-list",
    ),
    path(
        "download-payment-plan-payment-summary-pdf/<str:payment_plan_id>",
        hct_mis_api.apps.payment.views.download_payment_plan_summary_pdf,
        name="download-payment-plan-summary-pdf",
    ),
    path(
        "download-sanction-template",
        hct_mis_api.apps.sanction_list.views.download_sanction_template,
    ),
    path(
        "dashboard-report/<uuid:report_id>",
        hct_mis_api.apps.core.views.download_dashboard_report,
        name="dashboard_report",
    ),
    path(
        f"{settings.ADMIN_PANEL_URL}/download-target-population-xlsx/<uuid:target_population_id>/",
        hct_mis_api.apps.targeting.views.download_xlsx_households,
        name="admin-download-target-population",
    ),
    path(
        "download-survey-sample/<str:survey_id>",
        hct_mis_api.apps.accountability.views.download_cash_plan_payment_verification,
        name="download-survey-sample",
    ),
    path(f"{settings.ADMIN_PANEL_URL}/hijack/", include("hijack.urls")),
    path(f"{settings.ADMIN_PANEL_URL}/adminactions/", include("adminactions.urls")),
    path(
        f"{settings.ADMIN_PANEL_URL}/advanced_filters/",
        include("advanced_filters.urls"),
    ),
    path(
        "changelog/",
        include("hct_mis_api.apps.changelog.urls"),
    ),
    path(f"{settings.ADMIN_PANEL_URL}/", admin.site.urls),
    path("hh-status", hct_mis_api.apps.household.views.HouseholdStatusView.as_view()),
    path("upload-file/", UploadFile.as_view(), name="upload-file"),
    path("aurora/", include("hct_mis_api.contrib.aurora.urls", namespace="aurora")),
]

if settings.PROFILING:
    api_patterns.append(path("silk/", include("silk.urls", namespace="silk")))

if settings.CYPRESS_TESTING:
    api_patterns.append(path("cypress/", handle_cypress_command))
    api_patterns.append(path("cypress/xlsx/<int:seed>/", get_cypress_xlsx_file))

urlpatterns = (
    [
        path("_health", homepage),
        path("api/", include(api_patterns)),
    ]
    + staticfiles_urlpatterns()
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + [
        re_path(r"^(?!api/).*$", react_main, name="react-main"),
    ]
)

if settings.DEBUG and not settings.IS_TEST:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
