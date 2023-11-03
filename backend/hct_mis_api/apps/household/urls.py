from django.urls import path

from hct_mis_api.apps.household.views import HouseholdsTableView, IndividualsTableView

app_name = "household"
urlpatterns = [
    path("households-table/", HouseholdsTableView.as_view(), name="households-table"),
    path("individuals-table/", IndividualsTableView.as_view(), name="individuals-table"),
]
