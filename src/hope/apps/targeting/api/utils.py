import uuid

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.models import PaymentPlan


def get_field_by_name(field_name: str, payment_plan: PaymentPlan) -> dict:
    scopes = [Scope.TARGETING]
    if payment_plan.is_social_worker_program:
        scopes.append(Scope.XLSX_PEOPLE)
    factory = FieldFactory.from_only_scopes(scopes)
    factory.apply_business_area(payment_plan.business_area.slug)
    field = factory.to_dict_by("name")[field_name]
    choices = field.get("choices") or field.pop("_choices", None)
    if choices and callable(choices):
        field["choices"] = choices()
    field["id"] = uuid.uuid4()
    return field


def filter_choices(field: dict | None, args: list) -> dict | None:
    if not field:
        return None
    choices = field.get("choices")
    if args and choices:
        field["choices"] = list(filter(lambda choice: str(choice["value"]) in args, choices))
    return field
