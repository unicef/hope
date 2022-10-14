from adminactions.actions import find_duplicates_action, mass_update

from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.household.models import Individual


class IndividualAdmin(BAModelAdmin):
    model = Individual
    target_field = "business_area__slug"
    search_fields = ("^full_name",)
    list_display = [
        "full_name",
        "household",
    ]
    writeable_fields = []
    exclude = (
        "version",
        # "deduplication_golden_record_results",
        # "deduplication_batch_results",
        # "deduplication_batch_Status",
    )
    list_filter = (
        "duplicate",
        "withdrawn",
    )
    mass_update_exclude = [
        "business_area",
    ]
    actions = [mass_update, find_duplicates_action]
    list_select_related = ["household"]
