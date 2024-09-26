from django.urls import path

from rest_framework.routers import DefaultRouter

from hct_mis_api.apps.dashboard.views import (
    CreateOrUpdateDashReportView,
    DashboardReportdView,
)

router = DefaultRouter()
urlpatterns = [
    path("generate/<slug:business_area_slug>/", CreateOrUpdateDashReportView.as_view(), name="generate-dashreport"),
    path("<slug:business_area_slug>/", DashboardReportdView.as_view(), name="household-data"),
] + router.urls
