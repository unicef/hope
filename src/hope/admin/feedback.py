from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.accountability.models import Feedback


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
    raw_id_fields = [
        "business_area",
        "household_lookup",
        "individual_lookup",
        "admin2",
        "program",
        "created_by",
        "linked_grievance",
        "copied_from",
    ]
