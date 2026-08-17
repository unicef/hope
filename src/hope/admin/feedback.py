from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase, ViewOnUiMixin
from hope.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(ViewOnUiMixin, HOPEModelAdminBase):
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
    readonly_fields = ("unicef_id",)
    search_fields = ("unicef_id",)

    def frontend_url(self, obj: Feedback) -> str | None:
        if not obj.program:
            return None
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/accountability/feedback/{obj.id}"
