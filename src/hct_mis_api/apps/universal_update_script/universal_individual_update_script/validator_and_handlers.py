from datetime import date
from typing import Any, Optional

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import timezone_datetime
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import SEX_CHOICE
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.phone import is_valid_phone_number


def handle_date_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Optional[date]:
    if value is None or value == "":
        return None
    return timezone_datetime(value).date()


def handle_simple_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    return value

def handle_boolean_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    return value == "TRUE"

def handle_admin_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Optional[Area]:
    if value is None or value == "":
        return None
    return Area.objects.get(p_code=value)


def validate_admin(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    countries = business_area.countries.all()
    if not Area.objects.filter(p_code=value, area_type__country__in=countries).exists():
        return f"Administrative area {name} with p_code {value} not found"
    return None


def validate_string(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    return None


def validate_date(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        timezone_datetime(value).date()
    except Exception:
        return f"{value} for column {name} is not a valid date"
    return None

def validate_integer(value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        int(value)
    except Exception:
        return f"{value} for column {name} is not a valid integer"
    return None

def validate_phone_number(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    is_valid = is_valid_phone_number(value)
    if not is_valid:
        return f"{value} for column {name} is not a valid phone number"
    return None

def validate_choices(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    choices = _get_field_choices_values(modified_object, name)
    if value not in choices:
        return f"Invalid value {value} for column {name} allowed values are {choices}"
    return None

def validate_boolean(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    if value not in ["TRUE", "FALSE"]:
        return f"{value} for column {name} is not a valid boolean allowed values are TRUE or FALSE"
    return None

def _get_field_choices_values(instance, field_name):
    model_class = type(instance)
    field = model_class._meta.get_field(field_name)
    if field.choices:
        return [display for key, display in field.choices]
    return []

def validate_flex_field_string(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    return None
