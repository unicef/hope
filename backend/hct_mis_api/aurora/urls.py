from django.urls import path

from hct_mis_api.aurora.views import FetchDataView, RegistrationDataView

app_name = "aurora"

urlpatterns = [
    path("data/", RegistrationDataView.as_view(), name="data"),
    path("fetch/", FetchDataView.as_view(), name="app_index"),
]
