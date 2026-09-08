from django.urls import path

from hope.apps.dashboard.views import (
    CreateOrUpdateDashReportView,
    DashboardDataView,
    DashboardReportView,
)

urlpatterns = [
    path(
        "generate/<slug:business_area_slug>/",
        CreateOrUpdateDashReportView.as_view(),
        name="generate-dashreport",
    ),
    path(
        "<slug:business_area_slug>/data/",
        DashboardDataView.as_view(),
        name="household-data",
    ),
    path("<slug:business_area_slug>/", DashboardReportView.as_view(), name="dashboard"),
]
