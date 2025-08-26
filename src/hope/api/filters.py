from django_filters import (
    CharFilter,
    ChoiceFilter,
    DateTimeFromToRangeFilter,
    NumberFilter,
)
from django_filters.rest_framework import FilterSet

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models.country import Country
from hope.models.area import Area
from hope.models.area_type import AreaType
from hope.models import FinancialInstitution
from hope.contrib.aurora.models import Project, Registration


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


class ProjectFilter(FilterSet):
    org_slug = CharFilter(field_name="organization__slug", lookup_expr="exact")
    org_pk = CharFilter(field_name="organization__pk", lookup_expr="exact")

    class Meta:
        model = Project
        fields = ("org_slug", "org_pk")


class RegistrationFilter(FilterSet):
    org_slug = CharFilter(field_name="project__organization__slug", lookup_expr="exact")
    org_pk = CharFilter(field_name="project__organization__pk", lookup_expr="exact")
    programme_pk = CharFilter(field_name="project__programme__pk", lookup_expr="exact")

    class Meta:
        model = Registration
        fields = ("org_slug", "org_pk", "programme_pk")


class FinancialInstitutionFilter(UpdatedAtFilter):
    type = ChoiceFilter(choices=FinancialInstitution.FinancialInstitutionType.choices)

    class Meta:
        model = FinancialInstitution
        fields = ("type",)
