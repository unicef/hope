import datetime as dt
import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db.models import Q

from dateutil.relativedelta import relativedelta

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


def age_to_birth_date_range_query(field_name: str, age_min: Optional[int], age_max: Optional[int]) -> Q:
    query_dict = {}
    current_date = dt.date.today()
    if age_min is not None:
        query_dict[f"{field_name}__lte"] = current_date - relativedelta(years=+age_min)
    if age_max is not None:
        query_dict[f"{field_name}__gt"] = current_date - relativedelta(years=+age_max + 1)
    return Q(**query_dict)


def age_to_birth_date_query(comparison_method: str, args: Any) -> Q:
    field_name = "birth_date"
    comparison_method_args_count = {
        "RANGE": 2,
        "NOT_IN_RANGE": 2,
        "EQUALS": 1,
        "NOT_EQUALS": 1,
        "GREATER_THAN": 1,
        "LESS_THAN": 1,
    }
    args_count = comparison_method_args_count.get(comparison_method)
    if args_count is None:
        logger.error(f"Age filter query don't supports {comparison_method} type")
        raise ValidationError(f"Age filter query don't supports {comparison_method} type")
    if len(args) != args_count:
        logger.error(f"Age {comparison_method} filter query expect {args_count} arguments")
        raise ValidationError(f"Age {comparison_method} filter query expect {args_count} arguments")
    if comparison_method == "RANGE":
        return age_to_birth_date_range_query(field_name, *args)
    if comparison_method == "NOT_IN_RANGE":
        return ~(age_to_birth_date_range_query(field_name, *args))
    if comparison_method == "EQUALS":
        return age_to_birth_date_range_query(field_name, args[0], args[0])
    if comparison_method == "NOT_EQUALS":
        return ~(age_to_birth_date_range_query(field_name, args[0], args[0]))
    if comparison_method == "GREATER_THAN":
        return age_to_birth_date_range_query(field_name, args[0], None)
    if comparison_method == "LESS_THAN":
        return age_to_birth_date_range_query(field_name, None, args[0])
    logger.error(f"Age filter query don't supports {comparison_method} type")
    raise ValidationError(f"Age filter query don't supports {comparison_method} type")


def get_birth_certificate_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0])


def get_tax_id_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_TAX_ID, args[0])


def get_drivers_license_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0])


def get_national_id_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_NATIONAL_ID, args[0])


def get_national_passport_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0])


def get_electoral_card_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0])


def get_other_document_number_query(_: Any, args: Any) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_OTHER, args[0])


def get_documents_number_query(document_type: str, number: str) -> Q:
    return Q(documents__type__type=document_type, documents__document_number=number)


def get_birth_certificate_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0])


def get_tax_id_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_TAX_ID, args[0])


def get_drivers_licensee_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0])


def get_national_id_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_NATIONAL_ID, args[0])


def get_national_passport_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0])


def get_electoral_card_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0])


def get_other_issuer_query(_: Any, args: Any) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_OTHER, args[0])


def get_documents_issuer_query(document_type: str, country_alpha3: str) -> Q:
    return Q(documents__type__type=document_type, documents__type__country__iso_code3=country_alpha3)


def get_role_query(_: Any, args: Any) -> Q:
    return Q(households_and_roles__role=args[0])


def get_scope_id_number_query(_: Any, args: Any) -> Q:
    return Q(identities__partner__name=WFP, identities__number=args[0])


def get_scope_id_issuer_query(_: Any, args: Any) -> Q:
    return Q(identities__partner__name=WFP, identities__country__iso_code3=args[0])


def get_unhcr_id_number_query(_: Any, args: Any) -> Q:
    return Q(identities__partner__name=UNHCR, identities__number=args[0])


def get_unhcr_id_issuer_query(_: Any, args: Any) -> Q:
    return Q(identities__partner__name=UNHCR, identities__country__iso_code3=args[0])


def get_has_phone_number_query(_: Any, args: Any) -> Q:
    has_phone_no = args[0] in [True, "True"]
    return ~Q(phone_no="") if has_phone_no else Q(phone_no="")


def get_has_bank_account_number_query(_: Any, args: Any) -> Q:
    has_bank_account_number = args[0] in [True, "True"]
    if has_bank_account_number:  # Individual can have related object bank_account, but empty number
        return Q(bank_account_info__isnull=False) & ~Q(bank_account_info__bank_account_number="")
    return Q(bank_account_info__isnull=True) | Q(bank_account_info__bank_account_number="")


def get_has_tax_id_query(_: Any, args: Any) -> Q:
    has_tax_id = args[0] in [True, "True"]
    return Q(documents__type__key__iexact="TAX_ID") if has_tax_id else ~Q(documents__type__key__iexact="TAX_ID")


def country_generic_query(comparison_method: str, args: Any, lookup: Any) -> Q:
    query = Q(**{lookup: Countries.get_country_value(args[0])})
    if comparison_method == "EQUALS":
        return query
    elif comparison_method == "NOT_EQUALS":
        return ~query
    logger.error(f"Country filter query does not support {comparison_method} type")
    raise ValidationError(f"Country filter query does not support {comparison_method} type")


def country_query(comparison_method: str, args: Any) -> Q:
    return country_generic_query(comparison_method, args, "country")


def country_origin_query(comparison_method: str, args: Any) -> Q:
    return country_generic_query(comparison_method, args, "country_origin")


def registration_data_import_query(comparison_method: str, args: Any) -> Q:
    from django.db.models import Q

    return Q(registration_data_import__pk__in=args)
