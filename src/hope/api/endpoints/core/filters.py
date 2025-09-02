from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models.business_area import BusinessArea


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)
