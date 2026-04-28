from typing import Any
from uuid import UUID

from django.db import transaction
from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import (
    AreaLimitKeyBit,
    KeyConstructorMixin,
    get_or_create_cache_key,
    increment_cache_key,
)

HOUSEHOLD_LIST_PROGRAM_KEY = "{program_id}:households_list:version"
INDIVIDUAL_LIST_PROGRAM_KEY = "{program_id}:individuals_list:version"


def get_household_list_program_key(program_id: Any) -> Any:
    return get_or_create_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id=program_id), 0)


def increment_household_list_program_key(program_id: Any) -> int:
    return increment_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id=program_id))


def get_individual_list_program_key(program_id: Any) -> Any:
    return get_or_create_cache_key(INDIVIDUAL_LIST_PROGRAM_KEY.format(program_id=program_id), 0)


def increment_individual_list_program_key(program_id: Any) -> int:
    return increment_cache_key(INDIVIDUAL_LIST_PROGRAM_KEY.format(program_id=program_id))


def invalidate_household_list_cache(program_id: UUID) -> None:
    """Invalidate household list cache for a program.

    Call explicitly after Household.objects.filter(...).update(...)
    since .update() bypasses post_save signals.
    """
    transaction.on_commit(lambda: increment_household_list_program_key(program_id))


def invalidate_individual_list_cache(program_id: UUID) -> None:
    """Invalidate individual list cache for a program.

    Call explicitly after Individual.objects.filter(...).update(...)
    since .update() bypasses post_save signals.
    """
    transaction.on_commit(lambda: increment_individual_list_program_key(program_id))


def invalidate_household_and_individual_list_cache(program_id: UUID) -> None:
    """Invalidate both household and individual list caches for a program."""
    invalidate_household_list_cache(program_id)
    invalidate_individual_list_cache(program_id)


class HouseholdListKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        return str(get_household_list_program_key(view_instance.program.id))


class IndividualListKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        return str(get_individual_list_program_key(view_instance.program.id))


class HouseholdListKeyConstructor(KeyConstructorMixin):
    household_list = HouseholdListKeyBit()
    area_limits = AreaLimitKeyBit()


class IndividualListKeyConstructor(KeyConstructorMixin):
    individual_list = IndividualListKeyBit()
    area_limits = AreaLimitKeyBit()
