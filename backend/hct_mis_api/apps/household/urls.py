from django.urls import path

from hct_mis_api.apps.household.views import HouseholdsTableView, IndividualsTableView

app_name = "household"
urlpatterns = [
    path("households_table/", HouseholdsTableView.as_view(), name="households_table"),
    path("individuals_table/", IndividualsTableView.as_view(), name="individuals_table"),
]
