from datetime import date
from typing import Any, Callable, cast

from django.db.models import Model
from phonenumber_field.phonenumber import PhoneNumber

from hope.apps.core.utils import timezone_datetime
from hope.apps.utils.phone import is_valid_phone_number
from hope.models import Area, BusinessArea, Facility, Program
from hope.models.currency import Currency


def handle_date_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> date | None:
    if value is None or value == "":
        return None
    return timezone_datetime(value).date()


def handle_simple_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    return value


def handle_boolean_field(value: Any, name: str, household: Any, business_area: BusinessArea, program: Program) -> Any:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return value == "TRUE"


def handle_integer_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def handle_admin_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Area | None:
    if value is None or value == "":
        return None
    return Area.objects.get(p_code=value)


def handle_currency_field(
    value: Any, name: str, household: Any, business_area: BusinessArea, program: Program
) -> Currency | None:
    if value is None or value == "":
        return None
    return Currency.objects.get(code=value)


def validate_admin(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    countries = business_area.countries.all()
    if not Area.objects.filter(p_code=value, area_type__country__in=countries).exists():
        return f"Administrative area {name} with p_code {value} not found"
    return None


FACILITY_ADMIN_P_CODE_COLUMN = "facility_admin_p_code"


def handle_facility_field(  # noqa: PLR0913
    value: Any,
    name: str,
    household: Any,
    business_area: BusinessArea,
    program: Program,
    admin_p_code: Any = None,
) -> Facility | None:
    if value is None or value == "":
        return None
    return Facility.objects.get(
        name=value,
        business_area=business_area,
        admin_area__p_code=admin_p_code,
    )


def validate_facility(  # noqa: PLR0913
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
    admin_p_code: Any = None,
) -> str | None:
    if value is None or value == "":
        return None
    if admin_p_code is None or admin_p_code == "":
        return f"Column {FACILITY_ADMIN_P_CODE_COLUMN} is required when {name} is set"
    if not Facility.objects.filter(
        name=value,
        business_area=business_area,
        admin_area__p_code=admin_p_code,
    ).exists():
        return (
            f"Facility with name {value} and admin_area p_code {admin_p_code} "
            f"not found in business area {business_area.slug}"
        )
    return None


def validate_currency(
    value: Any, name: str, model_class: Any, business_area: BusinessArea, program: Program
) -> str | None:
    if value is None or value == "":
        return None
    if not Currency.objects.filter(code=value).exists():
        return f"Invalid currency code {value}"
    return None


def validate_string(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    return None


def validate_date(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    try:
        timezone_datetime(value).date()
    except ValueError:
        return f"{value} for column {name} is not a valid date"
    return None


def validate_integer(
    value: Any,
    name: str,
    modified_object: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    try:
        int(value)
    except (ValueError, TypeError):
        return f"{value} for column {name} is not a valid integer"
    return None


def validate_phone_number(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    is_valid = is_valid_phone_number(value)
    if not is_valid:
        return f"{value} for column {name} is not a valid phone number"
    return None


def _get_field_choices_values(model_class: type[Model], field_name: str) -> list[tuple[str, str]]:
    field = model_class._meta.get_field(field_name)
    if field.choices:
        return [key for key, display in field.choices]
    return []


def validate_choices(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    choices = _get_field_choices_values(model_class, name)
    if value not in choices:
        return f"Invalid value {value} for column {name} allowed values are {choices}"
    return None


def validate_boolean(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if value not in ["TRUE", "FALSE"]:
        return f"{value} for column {name} is not a valid boolean allowed values are TRUE or FALSE"
    return None


def validate_flex_field_string(
    value: Any,
    name: str,
    model_class: Any,
    business_area: BusinessArea,
    program: Program,
) -> str | None:
    return None


def boolean_generator_handler(value: Any) -> Any:
    return "TRUE" if value else "FALSE"


def simple_generator_handler(value: Any) -> Any:
    return value


GENERATOR_TYPE_HANDLER = {
    bool: boolean_generator_handler,
    Area: lambda value: value.p_code,
    Facility: lambda value: value.name,
    PhoneNumber: str,
    Currency: lambda value: value.code,
}


def get_generator_handler(value: Any) -> Callable:
    return cast("Callable", GENERATOR_TYPE_HANDLER.get(type(value), simple_generator_handler))
