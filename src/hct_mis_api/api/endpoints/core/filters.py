from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)
