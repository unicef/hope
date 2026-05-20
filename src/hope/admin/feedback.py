from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "issue_type",
        "business_area",
        "area",
        "consent",
        "household_lookup",
        "individual_lookup",
    )
    list_filter = ("issue_type", ("business_area", AutoCompleteFilter), "consent")
    search_fields = ("unicef_id",)
