from __future__ import absolute_import

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from core.views import homepage


urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("", homepage),
    path("_health", homepage),
    path("api/_health", homepage),
    path(
        "api/graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))
    ),
    path("api/", include("social_django.urls", namespace="social")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
