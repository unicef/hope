import logging
from datetime import date, datetime

from dateutil.parser import parse

from hct_mis_api.apps.core.core_fields_attributes import (
    TYPE_BOOL,
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    TYPE_STRING,
)
from hct_mis_api.apps.core.utils import (
    get_combined_attributes,
    serialize_flex_attributes,
)
from hct_mis_api.apps.geo.models import Area

logger = logging.getLogger(__name__)


def is_flex_field_attr(field):
    return field.endswith(("_i_f", "_h_f"))


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

        value_type = self.COMBINED_FIELDS[header]["type"]

        if value_type == TYPE_STRING:
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            return str(value)

        if value_type == TYPE_INTEGER:
            return int(value)

        if value_type == TYPE_DECIMAL:
            return float(value)

        if value_type in (TYPE_SELECT_ONE, TYPE_SELECT_MANY):
            custom_cast_method = self.COMBINED_FIELDS[header].get("custom_cast_value")

            if custom_cast_method:
                return custom_cast_method(input_value=value)

            choices = [x.get("value") for x in self.COMBINED_FIELDS[header]["choices"]]

            if value_type == TYPE_SELECT_MANY:
                if "," in value:
                    values = value.split(",")
                elif ";" in value:
                    values = value.split(";")
                else:
                    values = value.split(" ")
                valid_choices = []
                for single_choice in values:
                    if isinstance(single_choice, str):
                        without_trailing_whitespace = single_choice.strip()
                        if without_trailing_whitespace in choices:
                            valid_choices.append(without_trailing_whitespace)
                            continue
                        upper_value = without_trailing_whitespace.upper()
                        if upper_value in choices:
                            valid_choices.append(upper_value)
                            continue

                    if single_choice not in choices:
                        try:
                            valid_choices.append(int(single_choice))
                        except ValueError:
                            valid_choices.append(str(single_choice))
                return valid_choices
            else:
                if is_flex_field_attr(header):
                    if isinstance(value, float) and value.is_integer():
                        value = int(value)
                    value = str(value)
                if isinstance(value, str):
                    without_trailing_whitespace = value.strip()
                    if without_trailing_whitespace in choices:
                        return without_trailing_whitespace

                    upper_value = without_trailing_whitespace.upper()
                    if upper_value in choices:
                        return upper_value

                if value not in choices:
                    try:
                        return int(value)
                    except ValueError:
                        return str(value)

        if value_type == TYPE_DATE:
            if isinstance(value, (date, datetime)):
                return value

            if isinstance(value, str):
                return parse(value)

        if value_type == TYPE_BOOL:
            if isinstance(value, str):
                if value.lower() == "false":
                    return False
                elif value.lower() == "true":
                    return True

        return value
