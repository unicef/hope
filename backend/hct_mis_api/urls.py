from __future__ import absolute_import

from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from graphene_django.views import GraphQLView

from core.views import homepage, schema


def test_raise_exception_view(request):
    raise Exception('Testing Error Reporting')


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('', homepage),
    path('api/graphql', GraphQLView.as_view(graphiql=True)),
    path('api/graphql/schema.graphql', schema),
    path('api/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
