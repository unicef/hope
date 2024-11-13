from django_filters import CharFilter, DateTimeFromToRangeFilter, NumberFilter

from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
from hct_mis_api.apps.geo.models import Area, AreaType, Country


class CountryFilter(UpdatedAtFilter):
    valid_from = DateTimeFromToRangeFilter(field_name="valid_from")
    valid_until = DateTimeFromToRangeFilter(field_name="valid_until")

    class Meta:
        model = Country
        fields = ("valid_from", "valid_until")


class AreaFilter(UpdatedAtFilter):
    valid_from = DateTimeFromToRangeFilter(field_name="valid_from")
    valid_until = DateTimeFromToRangeFilter(field_name="valid_until")
    country_iso_code2 = CharFilter(field_name="area_type__country__iso_code2")
    country_iso_code3 = CharFilter(field_name="area_type__country__iso_code3")
    area_type_area_level = NumberFilter(field_name="area_type__area_level")
    parent_id = CharFilter(field_name="parent__id")
    parent_p_code = CharFilter(field_name="parent__p_code")

    class Meta:
        model = Area
        fields = (
            "country_iso_code2",
            "country_iso_code3",
            "area_type_area_level",
            "valid_from",
            "valid_until",
            "parent_id",
            "parent_p_code",
        )


class AreaTypeFilter(UpdatedAtFilter):
    country_iso_code2 = CharFilter(field_name="country__iso_code2")
    country_iso_code3 = CharFilter(field_name="country__iso_code3")
    parent_area_level = NumberFilter(field_name="parent__area_level")

    class Meta:
        model = AreaType
        fields = (
            "country_iso_code2",
            "country_iso_code3",
            "area_level",
            "parent_area_level",
        )
