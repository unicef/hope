from typing import Any

from django.db.models import QuerySet

from hct_mis_api.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin,
)
from hct_mis_api.apps.household.models import Household, Individual


class HouseholdListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "household_list"

    def _get_queryset(
        self, business_area_slug: Any | None, program_slug: Any | None, view_instance: Any | None
    ) -> QuerySet:
        return Household.all_merge_status_objects.filter(
            program__slug=program_slug,
            business_area__slug=business_area_slug,
        )


class IndividualListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "individual_list"

    def _get_queryset(
        self, business_area_slug: Any | None, program_slug: Any | None, view_instance: Any | None
    ) -> QuerySet:
        return Individual.all_merge_status_objects.filter(
            program__slug=program_slug,
            business_area__slug=business_area_slug,
        )


class HouseholdListKeyConstructor(KeyConstructorMixin):
    household_list = HouseholdListKeyBit()
    area_limits = AreaLimitKeyBit()


class IndividualListKeyConstructor(KeyConstructorMixin):
    individual_list = IndividualListKeyBit()
    area_limits = AreaLimitKeyBit()
