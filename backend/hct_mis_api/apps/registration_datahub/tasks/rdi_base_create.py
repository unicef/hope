import logging
from functools import reduce
from typing import List

from backend.hct_mis_api.apps.registration_datahub.value_caster import BaseValueCaster

from hct_mis_api.apps.core.utils import (
    get_combined_attributes,
    serialize_flex_attributes,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.registration_datahub.value_caster import (
    BooleanValueCaster,
    DateValueCaster,
    DecimalValueCaster,
    DefaultValueCaster,
    IntegerValueCaster,
    SelectManyValueCaster,
    SelectOneValueCaster,
    StringValueCaster,
)

logger = logging.getLogger(__name__)


class RdiBaseCreateTask:
    COMBINED_FIELDS = get_combined_attributes()
    FLEX_FIELDS = serialize_flex_attributes()

    @staticmethod
    def _assign_admin_areas_titles(household_obj):
        if household_obj.admin1:
            admin_area_level_1 = Area.objects.filter(p_code=household_obj.admin1).first()
            household_obj.admin1_title = getattr(admin_area_level_1, "name", "")
        if household_obj.admin2:
            admin_area_level_2 = Area.objects.filter(p_code=household_obj.admin2).first()
            household_obj.admin2_title = getattr(admin_area_level_2, "name", "")

        return household_obj

    def _cast_value(self, value, header):
        if isinstance(value, str):
            value = value.strip()

        if not value:
            return value

        field = self.COMBINED_FIELDS[header]

        casters: List[BaseValueCaster] = [
            DefaultValueCaster,
            BooleanValueCaster,
            SelectOneValueCaster,
            SelectManyValueCaster,
            DecimalValueCaster,
            IntegerValueCaster,
            DateValueCaster,
            StringValueCaster,
        ]

        value_caster = reduce(lambda next_caster, caster: caster(next_caster), casters)
        return value_caster.cast(field, value)
