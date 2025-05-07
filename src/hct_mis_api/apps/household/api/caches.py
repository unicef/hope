from typing import Any, Optional

from django.db.models import QuerySet

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import (
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin, AreaLimitKeyBit,
)
from hct_mis_api.apps.household.models import Household, Individual


class HouseholdListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "household_list"

    def _get_queryset(
        self, business_area_slug: Optional[Any], program_slug: Optional[Any], view_instance: Optional[Any]
    ) -> QuerySet:
        return Household.all_merge_status_objects.filter(
            program__slug=program_slug,
            business_area__slug=business_area_slug,
        )


class IndividualListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "individual_list"

    def _get_queryset(
        self, business_area_slug: Optional[Any], program_slug: Optional[Any], view_instance: Optional[Any]
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
