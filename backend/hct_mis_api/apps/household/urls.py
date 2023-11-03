from django.urls import path

from hct_mis_api.apps.household.views import household_table_view

app_name = "household"
urlpatterns = [
    path("household_table/", household_table_view, name="household_table"),
]
