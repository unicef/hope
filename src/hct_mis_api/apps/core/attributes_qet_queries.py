import datetime as dt
import logging
from typing import Any

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


def age_to_birth_date_range_query(
    field_name: str, age_min: int | None, age_max: int | None, is_social_worker_query: bool = False
) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    query_dict = {}
    current_date = dt.date.today()
    if age_min is not None:
        query_dict[f"{lookup_prefix}{field_name}__lte"] = current_date - relativedelta(years=+age_min)
    if age_max is not None:
        query_dict[f"{lookup_prefix}{field_name}__gt"] = current_date - relativedelta(years=+age_max + 1)
    return Q(**query_dict)


def age_to_birth_date_query(comparison_method: str, args: Any, is_social_worker_query: bool = False) -> Q:
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
        logger.warning(f"Age filter query don't supports {comparison_method} type")
        raise ValidationError(f"Age filter query don't supports {comparison_method} type")
    if len(args) != args_count:
        logger.warning(f"Age {comparison_method} filter query expect {args_count} arguments")
        raise ValidationError(f"Age {comparison_method} filter query expect {args_count} arguments")
    if comparison_method == "RANGE":
        return age_to_birth_date_range_query(field_name, *args, is_social_worker_query=is_social_worker_query)
    if comparison_method == "NOT_IN_RANGE":
        return ~(age_to_birth_date_range_query(field_name, *args, is_social_worker_query=is_social_worker_query))
    if comparison_method == "EQUALS":
        return age_to_birth_date_range_query(
            field_name, args[0], args[0], is_social_worker_query=is_social_worker_query
        )
    if comparison_method == "NOT_EQUALS":
        return ~(
            age_to_birth_date_range_query(field_name, args[0], args[0], is_social_worker_query=is_social_worker_query)
        )
    if comparison_method == "GREATER_THAN":
        return age_to_birth_date_range_query(field_name, args[0], None, is_social_worker_query=is_social_worker_query)
    if comparison_method == "LESS_THAN":
        return age_to_birth_date_range_query(field_name, None, args[0], is_social_worker_query=is_social_worker_query)
    logger.warning(f"Age filter query don't supports {comparison_method} type")  # pragma: no cover
    raise ValidationError(f"Age filter query don't supports {comparison_method} type")  # pragma: no cover


def get_birth_certificate_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0], is_social_worker_query=is_social_worker_query
    )


def get_tax_id_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_TAX_ID, args[0], is_social_worker_query=is_social_worker_query
    )


def get_drivers_license_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0], is_social_worker_query=is_social_worker_query
    )


def get_national_id_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_NATIONAL_ID, args[0], is_social_worker_query=is_social_worker_query
    )


def get_national_passport_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0], is_social_worker_query=is_social_worker_query
    )


def get_electoral_card_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(
        IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0], is_social_worker_query=is_social_worker_query
    )


def get_other_document_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query(IDENTIFICATION_TYPE_OTHER, args[0], is_social_worker_query=is_social_worker_query)


def get_documents_number_query(document_type: str, number: str, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(
        **{
            f"{lookup_prefix}documents__type__key": document_type.lower(),
            f"{lookup_prefix}documents__document_number": number,
        }
    )


def get_birth_certificate_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, args[0], is_social_worker_query=is_social_worker_query
    )


def get_tax_id_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_TAX_ID, args[0], is_social_worker_query=is_social_worker_query
    )


def get_drivers_licensee_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_DRIVERS_LICENSE, args[0], is_social_worker_query=is_social_worker_query
    )


def get_national_id_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_NATIONAL_ID, args[0], is_social_worker_query=is_social_worker_query
    )


def get_national_passport_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_NATIONAL_PASSPORT, args[0], is_social_worker_query=is_social_worker_query
    )


def get_electoral_card_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(
        IDENTIFICATION_TYPE_ELECTORAL_CARD, args[0], is_social_worker_query=is_social_worker_query
    )


def get_other_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query(IDENTIFICATION_TYPE_OTHER, args[0], is_social_worker_query=is_social_worker_query)


def get_documents_issuer_query(document_type: str, country_alpha3: str, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(
        **{
            f"{lookup_prefix}documents__type__type": document_type,
            f"{lookup_prefix}documents__type__country__iso_code3": country_alpha3,
        }
    )


def get_role_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(**{f"{lookup_prefix}households_and_roles__role": args[0]})


def get_scope_id_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(**{f"{lookup_prefix}identities__partner__name": WFP, f"{lookup_prefix}identities__number": args[0]})


def get_scope_id_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(
        **{f"{lookup_prefix}identities__partner__name": WFP, f"{lookup_prefix}identities__country__iso_code3": args[0]}
    )


def get_unhcr_id_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(**{f"{lookup_prefix}identities__partner__name": UNHCR, f"{lookup_prefix}identities__number": args[0]})


def get_unhcr_id_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return Q(
        **{
            f"{lookup_prefix}identities__partner__name": UNHCR,
            f"{lookup_prefix}identities__country__iso_code3": args[0],
        }
    )


def get_receiver_poi_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_number_query("receiver_poi", args[0], is_social_worker_query=is_social_worker_query)


def get_receiver_poi_issuer_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    return get_documents_issuer_query("receiver_poi", args[0], is_social_worker_query=is_social_worker_query)


def get_has_phone_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    has_phone_no = args[0] in [True, "True"]
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return ~Q(**{f"{lookup_prefix}phone_no": ""}) if has_phone_no else Q(**{f"{lookup_prefix}phone_no": ""})


def get_has_bank_account_number_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    has_bank_account_number = args[0] in [True, "True"]
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    if has_bank_account_number:  # Individual can have related object bank_account, but empty number
        return Q(**{f"{lookup_prefix}accounts__account_type__key": "bank"})
    return ~Q(**{f"{lookup_prefix}accounts__account_type__key": "bank"})


def get_has_tax_id_query(_: Any, args: Any, is_social_worker_query: bool = False) -> Q:
    has_tax_id = args[0] in [True, "True"]
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    return (
        Q(**{f"{lookup_prefix}documents__type__key__iexact": "TAX_ID"})
        if has_tax_id
        else ~Q(**{f"{lookup_prefix}documents__type__key__iexact": "TAX_ID"})
    )


def country_generic_query(comparison_method: str, args: Any, lookup: Any, is_social_worker_query: bool = False) -> Q:
    lookup_prefix = "individuals__" if is_social_worker_query else ""
    query = Q(**{lookup_prefix + lookup: Countries.get_country_value(args[0])})
    if comparison_method == "EQUALS":
        return query
    if comparison_method == "NOT_EQUALS":
        return ~query
    logger.warning(f"Country filter query does not support {comparison_method} type")
    raise ValidationError(f"Country filter query does not support {comparison_method} type")


def country_query(comparison_method: str, args: Any, is_social_worker_query: bool = False) -> Q:
    return country_generic_query(comparison_method, args, "country", is_social_worker_query=is_social_worker_query)


def country_origin_query(comparison_method: str, args: Any, is_social_worker_query: bool = False) -> Q:
    return country_generic_query(
        comparison_method, args, "country_origin", is_social_worker_query=is_social_worker_query
    )


def registration_data_import_query(comparison_method: str, args: Any, is_social_worker_query: bool = False) -> Q:
    from django.db.models import Q

    return Q(registration_data_import__pk__in=args)


def extra_rdis_query(comparison_method: str, args: Any, is_social_worker_query: bool = False) -> Q:
    from django.db.models import Q

    return Q(extra_rdis__in=args)
