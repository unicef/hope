from datetime import date
from typing import Any

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import timezone_datetime
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import SEX_CHOICE
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.phone import is_valid_phone_number


def handle_date_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> date | None:
    if value is None or value == "":
        return None
    return timezone_datetime(value).date()


def handle_simple_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    return value


def handle_admin_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Area | None:
    if value is None or value == "":
        return None
    return Area.objects.get(p_code=value)


def validate_admin(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> str | None:
    if value is None or value == "":
        return None
    countries = business_area.countries.all()
    if not Area.objects.filter(p_code=value, area_type__country__in=countries).exists():
        return f"Administrative area {name} with p_code {value} not found"
    return None


def validate_string(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> str | None:
    return None


def validate_date(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> str | None:
    if value is None or value == "":
        return None
    try:
        timezone_datetime(value).date()
    except Exception:
        return f"{value} for column {name} is not a valid date"
    return None


def validate_phone_number(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> str | None:
    if value is None or value == "":
        return None
    is_valid = is_valid_phone_number(value)
    if not is_valid:
        return f"{value} for column {name} is not a valid phone number"
    return None


def validate_sex(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> str | None:
    if value is None or value == "":
        return None
    sex_choices = [value for value, _ in SEX_CHOICE]
    if value not in sex_choices:
        return f"Invalid value {value} for column {name}"
    return None


def validate_flex_field_string(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> str | None:
    return None
