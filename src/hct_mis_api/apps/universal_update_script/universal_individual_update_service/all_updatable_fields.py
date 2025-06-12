"""
This is static by design, it could be made dynamic by fetching the fields from the model itself.
"""
from typing import Any, Dict, List, Tuple, Type

from django.db.models import Model

from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.payment.models import DeliveryMechanismConfig
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
    handle_admin_field,
    handle_boolean_field,
    handle_date_field,
    handle_integer_field,
    handle_simple_field,
    validate_admin,
    validate_boolean,
    validate_choices,
    validate_date,
    validate_flex_field_string,
    validate_integer,
    validate_phone_number,
    validate_string,
)

individual_fields: Dict[str, Tuple[str, Any, Any]] = {
    # "photo": ("photo", validate_string, handle_simple_field), # TODO: Handle photo
    "full_name": ("full_name", validate_string, handle_simple_field),
    "given_name": ("given_name", validate_string, handle_simple_field),
    "middle_name": ("middle_name", validate_string, handle_simple_field),
    "family_name": ("family_name", validate_string, handle_simple_field),
    "sex": ("sex", validate_choices, handle_simple_field),
    "birth_date": ("birth_date", validate_date, handle_date_field),
    "estimated_birth_date": ("estimated_birth_date", validate_boolean, handle_boolean_field),
    "marital_status": ("marital_status", validate_string, handle_simple_field),
    "phone_no": ("phone_no", validate_phone_number, handle_simple_field),
    "phone_no_alternative": ("phone_no_alternative", validate_phone_number, handle_simple_field),
    "email": ("email", validate_string, handle_simple_field),
    "payment_delivery_phone_no": ("payment_delivery_phone_no", validate_phone_number, handle_simple_field),
    "relationship": ("relationship", validate_string, handle_simple_field),
    "work_status": ("work_status", validate_choices, handle_simple_field),
    "first_registration_date": ("first_registration_date", validate_date, handle_simple_field),
    "last_registration_date": ("last_registration_date", validate_date, handle_simple_field),
    "enrolled_in_nutrition_programme": ("enrolled_in_nutrition_programme", validate_boolean, handle_boolean_field),
    "pregnant": ("pregnant", validate_boolean, handle_boolean_field),
    "disability": ("disability", validate_choices, handle_simple_field),
    "observed_disability": ("observed_disability", validate_boolean, handle_boolean_field),
    # "disability_certificate_picture": ("disability_certificate_picture", validate_string, handle_simple_field), # TODO: Handle picture
    "seeing_disability": ("seeing_disability", validate_boolean, handle_boolean_field),
    "hearing_disability": ("hearing_disability", validate_boolean, handle_boolean_field),
    "physical_disability": ("physical_disability", validate_boolean, handle_boolean_field),
    "memory_disability": ("memory_disability", validate_boolean, handle_boolean_field),
    "selfcare_disability": ("selfcare_disability", validate_boolean, handle_boolean_field),
    "comms_disability": ("comms_disability", validate_boolean, handle_boolean_field),
    "who_answers_phone": ("who_answers_phone", validate_string, handle_simple_field),
    "who_answers_alt_phone": ("who_answers_alt_phone", validate_string, handle_simple_field),
    "fchild_hoh": ("fchild_hoh", validate_boolean, handle_boolean_field),
    "child_hoh": ("child_hoh", validate_boolean, handle_boolean_field),
    "preferred_language": ("preferred_language", validate_string, handle_simple_field),
    "age_at_registration": ("age_at_registration", validate_string, handle_simple_field),
}
household_fields: Dict[str, Tuple[str, Any, Any]] = {
    "consent": ("consent", validate_boolean, handle_boolean_field),
    # "consent_sharing": ("consent_sharing", validate_boolean, handle_boolean_field), # TODO handle multiselect
    "residence_status": ("residence_status", validate_choices, handle_simple_field),
    "country_origin": ("country_origin", validate_string, handle_simple_field),
    # "country": ("country", validate_string, handle_simple_field), # TODO: Handle country
    "address": ("address", validate_string, handle_simple_field),
    "zip_code": ("zip_code", validate_string, handle_simple_field),
    "admin_area": ("admin_area", validate_string, handle_simple_field),
    "admin1": ("admin1", validate_admin, handle_admin_field),
    "admin2": ("admin2", validate_string, handle_admin_field),
    "admin3": ("admin3", validate_string, handle_admin_field),
    "admin4": ("admin4", validate_string, handle_admin_field),
    "size": ("size", validate_integer, handle_integer_field),
    "female_age_group_0_5_count": ("female_age_group_0_5_count", validate_integer, handle_integer_field),
    "female_age_group_6_11_count": ("female_age_group_6_11_count", validate_integer, handle_integer_field),
    "female_age_group_12_17_count": ("female_age_group_12_17_count", validate_integer, handle_integer_field),
    "female_age_group_18_59_count": ("female_age_group_18_59_count", validate_integer, handle_integer_field),
    "female_age_group_60_count": ("female_age_group_60_count", validate_integer, handle_integer_field),
    "pregnant_count": ("pregnant_count", validate_integer, handle_integer_field),
    "male_age_group_0_5_count": ("male_age_group_0_5_count", validate_integer, handle_integer_field),
    "male_age_group_6_11_count": ("male_age_group_6_11_count", validate_integer, handle_integer_field),
    "male_age_group_12_17_count": ("male_age_group_12_17_count", validate_integer, handle_integer_field),
    "male_age_group_18_59_count": ("male_age_group_18_59_count", validate_integer, handle_integer_field),
    "male_age_group_60_count": ("male_age_group_60_count", validate_integer, handle_integer_field),
    "female_age_group_0_5_disabled_count": (
        "female_age_group_0_5_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "female_age_group_6_11_disabled_count": (
        "female_age_group_6_11_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "female_age_group_12_17_disabled_count": (
        "female_age_group_12_17_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "female_age_group_18_59_disabled_count": (
        "female_age_group_18_59_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "female_age_group_60_disabled_count": (
        "female_age_group_60_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "male_age_group_0_5_disabled_count": ("male_age_group_0_5_disabled_count", validate_integer, handle_integer_field),
    "male_age_group_6_11_disabled_count": (
        "male_age_group_6_11_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "male_age_group_12_17_disabled_count": (
        "male_age_group_12_17_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "male_age_group_18_59_disabled_count": (
        "male_age_group_18_59_disabled_count",
        validate_integer,
        handle_integer_field,
    ),
    "male_age_group_60_disabled_count": ("male_age_group_60_disabled_count", validate_integer, handle_integer_field),
    "children_count": ("children_count", validate_integer, handle_integer_field),
    "male_children_count": ("male_children_count", validate_integer, handle_integer_field),
    "female_children_count": ("female_children_count", validate_integer, handle_integer_field),
    "children_disabled_count": ("children_disabled_count", validate_integer, handle_integer_field),
    "male_children_disabled_count": ("male_children_disabled_count", validate_integer, handle_integer_field),
    "female_children_disabled_count": ("female_children_disabled_count", validate_integer, handle_integer_field),
    "returnee": ("returnee", validate_boolean, handle_boolean_field),
    "first_registration_date": ("first_registration_date", validate_date, handle_simple_field),
    "last_registration_date": ("last_registration_date", validate_date, handle_simple_field),
    "fchild_hoh": ("fchild_hoh", validate_boolean, handle_boolean_field),
    "child_hoh": ("child_hoh", validate_boolean, handle_boolean_field),
    "village": ("village", validate_string, handle_simple_field),
    "registration_method": ("registration_method", validate_choices, handle_simple_field),
    "currency": ("currency", validate_choices, handle_simple_field),
    "unhcr_id": ("unhcr_id", validate_string, handle_simple_field),
}


def get_individual_flex_fields() -> dict[Any, Any]:
    flex_fields_dict = dict()
    for flexible_attribute in FlexibleAttribute.objects.filter(
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    ):
        flex_fields_dict[f"flex_ind__{flexible_attribute.name}"] = (
            flexible_attribute.name,
            validate_flex_field_string,
            handle_simple_field,
        )
    return flex_fields_dict


def get_household_flex_fields() -> dict[Any, Any]:
    flex_fields_dict = dict()
    for flexible_attribute in FlexibleAttribute.objects.filter(
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
    ):
        flex_fields_dict[f"flex_hh__{flexible_attribute.name}"] = (
            flexible_attribute.name,
            validate_flex_field_string,
            handle_simple_field,
        )
    return flex_fields_dict


def get_document_fields() -> list[Any]:
    return [(f"{x}_no_i_c", f"{x}_country_i_c") for x in DocumentType.objects.values_list("key", flat=True)]


def get_account_fields() -> dict[Any, Any]:
    deliver_mechanism_data_fields = {}
    for dm_config in DeliveryMechanismConfig.objects.all():
        if not dm_config.delivery_mechanism.account_type:
            continue
        account_type = dm_config.delivery_mechanism.account_type.key
        wallet_fields = set()
        for field in dm_config.required_fields:
            wallet_fields.add((f"account__{account_type}__{field}", field))
        wallet_fields.add((f"account__{account_type}__*", None))
        wallet_fields.add((f"account__{account_type}__number", "number"))
        if len(wallet_fields) > 0:
            deliver_mechanism_data_fields[account_type] = tuple(wallet_fields)
    return deliver_mechanism_data_fields


def _get_db_fields(model_class: Type[Model]) -> List[str]:
    """
    Returns a list of field names that correspond to the columns stored
    in the model's database table, excluding related fields.
    """
    return [field.name for field in model_class._meta.fields]
