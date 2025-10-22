from django.urls import path

from .views import UploadFileView, download_sanction_template

app_name = "sanction"

urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="upload"),
    path("template/", download_sanction_template, name="download_sanction_template"),
]
