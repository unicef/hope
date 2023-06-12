from django.urls import path

from power_query.views import data, document, report, report_list

app_name = "power_query"

urlpatterns = [
    path("reports/", report_list, name="report_list"),
    path("report/<int:pk>/", report, name="report"),
    path("document/<int:report>/<int:pk>/", document, name="document"),
    path("data/<int:pk>/", data, name="data"),
]
