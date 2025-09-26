from typing import Any

from django.db.models import QuerySet
from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin,
    get_or_create_cache_key,
    increment_cache_key,
)
from hope.apps.household.models import Individual

HOUSEHOLD_LIST_PROGRAM_KEY = "{program_id}:households_list:version"


def get_household_list_program_key(program_id):
    return get_or_create_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id), 0)


def increment_household_list_program_key(program_id):
    return increment_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id))


class HouseholdListKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        return str(get_household_list_program_key(view_instance.program.id))


class IndividualListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "individual_list"

    def _get_queryset(
        self,
        business_area_slug: Any | None,
        program_slug: Any | None,
        view_instance: Any | None,
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
