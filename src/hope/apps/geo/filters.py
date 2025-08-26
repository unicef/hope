from django_filters import CharFilter, FilterSet

from hope.apps.core.filters import IntegerFilter
from hope.apps.core.utils import decode_id_string
from hope.models.area import Area


class AreaFilter(FilterSet):
    business_area = CharFilter(method="business_area_filter")
    level = IntegerFilter(
        field_name="area_type__area_level",
    )
    parent_id = CharFilter(method="parent_id_filter")

    class Meta:
        model = Area
        fields = {
            "name": ["exact", "istartswith"],
        }

    def business_area_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet":
        return qs.filter(area_type__country__business_areas__slug=value)

    def parent_id_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet":
        parent_id = decode_id_string(value)
        return qs.filter(parent_id=parent_id)
