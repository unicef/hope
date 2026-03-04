from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import (
    AreaLimitKeyBit,
    KeyConstructorMixin,
    get_or_create_cache_key,
    increment_cache_key,
)

HOUSEHOLD_LIST_PROGRAM_KEY = "{program_id}:households_list:version"
INDIVIDUAL_LIST_PROGRAM_KEY = "{program_id}:individuals_list:version"


def get_household_list_program_key(program_id):
    return get_or_create_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id=program_id), 0)


def increment_household_list_program_key(program_id):
    return increment_cache_key(HOUSEHOLD_LIST_PROGRAM_KEY.format(program_id=program_id))


def get_individual_list_program_key(program_id):
    return get_or_create_cache_key(INDIVIDUAL_LIST_PROGRAM_KEY.format(program_id=program_id), 0)


def increment_individual_list_program_key(program_id):
    return increment_cache_key(INDIVIDUAL_LIST_PROGRAM_KEY.format(program_id=program_id))


class HouseholdListKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):  # noqa: PLR0913 – override of base method signature
        return str(get_household_list_program_key(view_instance.program.id))


class IndividualListKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):  # noqa: PLR0913 – override of base method signature
        return str(get_individual_list_program_key(view_instance.program.id))


class HouseholdListKeyConstructor(KeyConstructorMixin):
    household_list = HouseholdListKeyBit()
    area_limits = AreaLimitKeyBit()


class IndividualListKeyConstructor(KeyConstructorMixin):
    individual_list = IndividualListKeyBit()
    area_limits = AreaLimitKeyBit()
