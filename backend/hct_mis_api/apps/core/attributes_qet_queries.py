import datetime as dt
import logging

from django.core.exceptions import ValidationError
from django.db.models import Q

from dateutil.relativedelta import relativedelta
from prompt_toolkit.validation import ValidationError  # noqa: F811 # TODO: bug?

from hct_mis_api.apps.core.countries import Countries
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DRIVERS_LICENSE,
    IDENTIFICATION_TYPE_ELECTORAL_CARD,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
    UNHCR,
    WFP,
)

logger = logging.getLogger(__name__)


def age_to_birth_date_range_query(field_name, age_min, age_max):
    query_dict = {}
    current_date = dt.date.today()
    if age_min is not None:
        query_dict[f"{field_name}__lte"] = current_date - relativedelta(years=+age_min)
    if age_max is not None:
        query_dict[f"{field_name}__gt"] = current_date - relativedelta(years=+age_max + 1)
    return Q(**query_dict)


def age_to_birth_date_query(comparision_method, args):
    field_name = "birth_date"
    comparision_method_args_count = {
        "RANGE": 2,
        "NOT_IN_RANGE": 2,
        "EQUALS": 1,
        "NOT_EQUALS": 1,
        "GREATER_THAN": 1,
        "LESS_THAN": 1,
    }
    args_count = comparision_method_args_count.get(comparision_method)
    if args_count is None:
        logger.error(f"Age filter query don't supports {comparision_method} type")
        raise ValidationError(f"Age filter query don't supports {comparision_method} type")
    if len(args) != args_count:
        logger.error(f"Age {comparision_method} filter query expect {args_count} arguments")
        raise ValidationError(f"Age {comparision_method} filter query expect {args_count} arguments")
    if comparision_method == "RANGE":
        return age_to_birth_date_range_query(field_name, *args)
    if comparision_method == "NOT_IN_RANGE":
        return ~(age_to_birth_date_range_query(field_name, *args))
    if comparision_method == "EQUALS":
        return age_to_birth_date_range_query(field_name, args[0], args[0])
    if comparision_method == "NOT_EQUALS":
        return ~(age_to_birth_date_range_query(field_name, args[0], args[0]))
    if comparision_method == "GREATER_THAN":
        return age_to_birth_date_range_query(field_name, args[0], None)
    if comparision_method == "LESS_THAN":
        return age_to_birth_date_range_query(field_name, None, args[0])
    logger.error(f"Age filter query don't supports {comparision_method} type")
    raise ValidationError(f"Age filter query don't supports {comparision_method} type")


def get_birth_certificate_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0])


def get_tax_id_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_TAX_ID, args[0])


def get_drivers_license_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0])


def get_national_id_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_NATIONAL_ID, args[0])


def get_national_passport_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0])


def get_electoral_card_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0])


def get_other_document_number_query(_, args):
    return get_documents_number_query(IDENTIFICATION_TYPE_OTHER, args[0])


def get_documents_number_query(document_type, number):
    return Q(documents__type__type=document_type, documents__document_number=number)


def get_birth_certificate_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0])


def get_tax_id_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_TAX_ID, args[0])


def get_drivers_licensee_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0])


def get_national_id_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_NATIONAL_ID, args[0])


def get_national_passport_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0])


def get_electoral_card_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0])


def get_other_issuer_query(_, args):
    return get_documents_issuer_query(IDENTIFICATION_TYPE_OTHER, args[0])


def get_documents_issuer_query(document_type, country_alpha3):
    return Q(documents__type__type=document_type, documents__type__country__iso_code3=country_alpha3)


def get_role_query(_, args):
    return Q(households_and_roles__role=args[0])


def get_scope_id_number_query(_, args):
    return Q(identities__agency__type=WFP, identities__number=args[0])


def get_scope_id_issuer_query(_, args):
    return Q(identities__agency__type=WFP, identities__agency__country__iso_code3=args[0])


def get_unhcr_id_number_query(_, args):
    return Q(identities__agency__type=UNHCR, identities__number=args[0])


def get_unhcr_id_issuer_query(_, args):
    return Q(identities__agency__type=UNHCR, identities__agency__country__iso_code3=args[0])


def get_has_phone_number_query(_, args):
    has_phone_no = args[0] in [True, "True"]
    return ~Q(phone_no="") if has_phone_no else Q(phone_no="")


def get_has_bank_account_number_query(_, args):
    has_bank_account_number = args[0] in [True, "True"]
    if has_bank_account_number:  # Individual can have related object bank_account, but empty number
        return Q(bank_account_info__isnull=False) & ~Q(bank_account_info__bank_account_number="")
    return Q(bank_account_info__isnull=True) | Q(bank_account_info__bank_account_number="")


def get_has_tax_id_query(_, args):
    has_tax_id = args[0] in [True, "True"]
    return Q(documents__type__type="TAX_ID") if has_tax_id else ~Q(documents__type__type="TAX_ID")


def country_generic_query(comparision_method, args, lookup):
    query = Q(**{lookup: Countries.get_country_value(args[0])})
    if comparision_method == "EQUALS":
        return query
    elif comparision_method == "NOT_EQUALS":
        return ~query
    logger.error(f"Country filter query does not support {comparision_method} type")
    raise ValidationError(f"Country filter query does not support {comparision_method} type")


def country_query(comparision_method, args):
    return country_generic_query(comparision_method, args, "country")


def country_origin_query(comparision_method, args):
    return country_generic_query(comparision_method, args, "country_origin")


def admin_area1_query(comparision_method, args):
    from django.db.models import Q

    return Q(Q(admin_area__p_code=args[0]) & Q(admin_area__area_type__area_level=1)) | Q(
        Q(admin_area__parent__p_code=args[0]) & Q(admin_area__parent__area_type__area_level=1)
    )


def registration_data_import_query(comparison_method, args):
    from django.db.models import Q

    return Q(registration_data_import__pk__in=args)
