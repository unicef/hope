from __future__ import absolute_import

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

import adminactions.actions as actions
from graphene_file_upload.django import FileUploadGraphQLView

import hct_mis_api.apps.account.views
import hct_mis_api.apps.payment.views
import hct_mis_api.apps.targeting.views
import hct_mis_api.apps.registration_datahub.views
import hct_mis_api.apps.sanction_list.views
from hct_mis_api.apps.core.views import (
    call_command_view,
    homepage,
    logout_view,
    schema,
    trigger_error,
)

# register all adminactions
actions.add_to_site(site, exclude=["export_delete_tree"])

urlpatterns = [
    path(f"api/{settings.ADMIN_PANEL_URL}/", admin.site.urls),
    path("api/explorer/", include("explorer.urls")),
    path(f"api/{settings.ADMIN_PANEL_URL}/hijack/", include("hijack.urls")),
    path(f"api/{settings.ADMIN_PANEL_URL}/adminactions/", include("adminactions.urls")),
    path(f"api/{settings.ADMIN_PANEL_URL}/advanced_filters/", include("advanced_filters.urls")),
    path(f"api/{settings.ADMIN_PANEL_URL}/reports/", include("hct_mis_api.apps.power_query.urls")),
    path("", homepage),
    path("_health", homepage),
    path("api/_health", homepage),
    path("api/graphql/schema.graphql", schema),
    path("api/graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path("api/", include("social_django.urls", namespace="social")),
    path("api/logout", logout_view),
    path("api/sentry-debug/", trigger_error),
    path("api/download-template", hct_mis_api.apps.registration_datahub.views.download_template),
    path(
        "api/download-exported-users/<str:business_area_slug>", hct_mis_api.apps.account.views.download_exported_users
    ),
    path(
        "api/download-cash-plan-payment-verification/<str:verification_id>",
        hct_mis_api.apps.payment.views.download_cash_plan_payment_verification,
    ),
    path(
        "api/download-sanction-template",
        hct_mis_api.apps.sanction_list.views.download_sanction_template,
    ),
    path(
        "api/unicorn/download-target-population-xlsx/<uuid:target_population_id>/",
        hct_mis_api.apps.targeting.views.download_xlsx_households,
        name="admin-download-target-population",
    ),
    path(
        "api/dashboard-report/<uuid:report_id>",
        hct_mis_api.apps.core.views.download_dashboard_report,
        name="dashboard_report",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
