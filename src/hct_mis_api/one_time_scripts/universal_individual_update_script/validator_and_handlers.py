from datetime import date
from typing import Any, Optional

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import timezone_datetime
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import FEMALE, MALE
from hct_mis_api.apps.program.models import Program


def handle_date_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Optional[date]:
    if value is None or value == "":
        return None
    return timezone_datetime(value).date()


def handle_simple_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    return value


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


def validate_sex(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    if value is None or value == "":
        return None
    sex_choices = [MALE, FEMALE]
    if value not in sex_choices:
        return f"Invalid value {value} for column {name}"
    return None


def validate_flex_field_string(
    value: Any, name: str, modified_object: Any, business_area: BusinessArea, program: Program
) -> Optional[str]:
    return None