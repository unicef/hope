from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase, ViewOnUiMixin
from hope.models import Survey


@admin.register(Survey)
class SurveyAdmin(ViewOnUiMixin, HOPEModelAdminBase):
    filter_horizontal = ["recipients"]
    list_display = (
        "unicef_id",
        "title",
        "category",
        "business_area",
        "program",
        "flow_id",
        "created_by",
        "sample_file",
        "sample_size",
    )
    readonly_fields = (
        "category",
        "created_by",
        "payment_plan",
        "program",
        "business_area",
    )
    list_filter = ("category", ("flow_id", AutoCompleteFilter))
    search_fields = ("unicef_id", "title")

    def frontend_url(self, obj: Survey) -> str | None:
        if not obj.program:
            return None
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/accountability/surveys/{obj.id}"
