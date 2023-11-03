from django.urls import path

from hct_mis_api.apps.household.views import HouseholdTableView

app_name = "household"
urlpatterns = [
    path("household_table/", HouseholdTableView.as_view(), name="household_table"),
]
