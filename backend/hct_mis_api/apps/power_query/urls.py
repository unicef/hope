from django.urls import path

from .views import api, report

app_name = "power_query"

urlpatterns = [
    path("report/<int:pk>/", report, name="report"),
    path("data/<int:pk>/", api),
]
