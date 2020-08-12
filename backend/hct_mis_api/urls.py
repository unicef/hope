from __future__ import absolute_import

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

import payment
import registration_datahub.views
import sanction_list.views
from core.views import (
    homepage,
    schema,
    trigger_error,
    logout_view,
    call_command_view,
)


urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/admin/call-command", call_command_view),
    path("", homepage),
    path("_health", homepage),
    path("api/_health", homepage),
    path("api/graphql/schema.graphql", schema),
    path(
        "api/graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))
    ),
    path("api/", include("social_django.urls", namespace="social")),
    path("api/logout", logout_view),
    path("api/sentry-debug/", trigger_error),
    path("api/download-template", registration_datahub.views.download_template),
    path("api/download_cash_plan_payment_verification/<uuid:verification_id>", payment.views.download_cash_plan_payment_verification),
    path(
        "api/download-sanction-template",
        sanction_list.views.download_sanction_template,
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
