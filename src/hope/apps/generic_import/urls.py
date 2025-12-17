from django.urls import path

from hope.apps.generic_import.views import GenericImportUploadView

app_name = "generic_import"

urlpatterns = [
    path("upload/", GenericImportUploadView.as_view(), name="generic-import"),
]
