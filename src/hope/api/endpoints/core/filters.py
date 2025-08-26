from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models.core import BusinessArea


class BusinessAreaFilter(UpdatedAtFilter):
    class Meta:
        model = BusinessArea
        fields = ("active",)
