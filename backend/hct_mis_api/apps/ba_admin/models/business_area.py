from hct_mis_api.apps.ba_admin.options import BAModelAdmin
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaAdmin(BAModelAdmin):
    model = BusinessArea
    target_field = "slug"

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs.filter(**self.get_business_area_filter(request))
