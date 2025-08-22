from adminactions import actions
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path

import hope.admin
import hope.apps.account.views
import hope.apps.accountability.views
import hope.apps.household.views
import hope.apps.payment.views
import hope.apps.registration_data.views
import hope.apps.sanction_list.views
import hope.apps.targeting.views
from hope.apps.core.rest_api import all_fields_attributes
from hope.apps.core.views import (
    UploadFile,
    homepage,
    logout_view,
    trigger_error,
)
from hope.apps.web.views import react_main

# register all adminactions
actions.add_to_site(site, exclude=["export_delete_tree"])

api_patterns = [
    path("rest/", include("hope.api.urls", namespace="api")),
    path("", include("social_django.urls", namespace="social")),
    path("fields_attributes/", all_fields_attributes, name="fields_attributes"),
    path("_health", homepage),
    path("explorer/", include("explorer.urls")),
    path("logout", logout_view, name="logout"),
    path("sentry-debug/", trigger_error),
    path(
        "program/<str:program_id>/download-template",
        hope.apps.registration_data.views.download_template,
    ),
    path(
        "download-exported-users/<str:business_area_slug>",
        hope.apps.account.views.download_exported_users,
    ),
    path(
        "download-payment-verification-plan/<str:verification_id>",
        hope.apps.payment.views.download_payment_verification_plan,
        name="download-payment-verification-plan",
    ),
    path(
        "download-payment-plan-payment-list/<str:payment_plan_id>",
        hope.apps.payment.views.download_payment_plan_payment_list,
        name="download-payment-plan-payment-list",
    ),
    path(
        "download-payment-plan-payment-summary-pdf/<str:payment_plan_id>",
        hope.apps.payment.views.download_payment_plan_summary_pdf,
        name="download-payment-plan-summary-pdf",
    ),
    path(
        "download-sanction-template",
        hope.apps.sanction_list.views.download_sanction_template,
    ),
    path(
        f"{settings.ADMIN_PANEL_URL}/download-target-population-xlsx/<uuid:target_population_id>/",
        hope.apps.targeting.views.download_xlsx_households,
        name="admin-download-target-population",
    ),
    path(
        "download-survey-sample/<str:survey_id>",
        hope.apps.accountability.views.download_cash_plan_payment_verification,
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
        include("hope.apps.changelog.urls"),
    ),
    path(f"{settings.ADMIN_PANEL_URL}/", admin.site.urls),
    path("sanction-list/", include("hope.apps.sanction_list.urls")),
    path("hh-status", hope.apps.household.views.HouseholdStatusView.as_view()),
    path("upload-file/", UploadFile.as_view(), name="upload-file"),
    path("aurora/", include("hope.contrib.aurora.urls", namespace="aurora")),
]

if settings.PROFILING:
    api_patterns.append(path("silk/", include("silk.urls", namespace="silk")))

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
