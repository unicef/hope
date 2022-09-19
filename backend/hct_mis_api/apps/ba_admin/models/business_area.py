from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaAdmin(BAModelAdmin):
    model = BusinessArea
    target_field = "slug"
    list_display = [
        "code",
        "name",
    ]
    exclude = ("custom_fields",)
    writeable_fields = [
        "postpone_deduplication",
        "deduplication_duplicate_score",
        "deduplication_possible_duplicate_score",
        "deduplication_batch_duplicates_percentage",
        "deduplication_batch_duplicates_allowed",
        "deduplication_golden_record_duplicates_percentage",
        "deduplication_golden_record_duplicates_allowed",
        "screen_beneficiary",
        "deduplication_ignore_withdraw",
    ]

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs.filter(**self.get_business_area_filter(request))
