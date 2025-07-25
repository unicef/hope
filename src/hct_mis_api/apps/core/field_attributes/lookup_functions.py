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
    Individual,
)


def get_birth_certificate_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)


def get_tax_id_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_TAX_ID)


def get_drivers_license_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_DRIVERS_LICENSE)


def get_electoral_card_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_ELECTORAL_CARD)


def get_national_passport_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_NATIONAL_PASSPORT)


def get_national_id_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_NATIONAL_ID)


def get_other_id_no(individual: Individual) -> str:
    return get_document_no(individual, IDENTIFICATION_TYPE_OTHER)


def get_document_no(individual: Individual, document_type: str) -> str:
    return getattr(individual.documents.filter(type__key=document_type.lower()).first(), "document_number", "")


def get_birth_certificate_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)


def get_tax_id_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_TAX_ID)


def get_drivers_license_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_DRIVERS_LICENSE)


def get_electoral_card_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_ELECTORAL_CARD)


def get_national_passport_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_NATIONAL_PASSPORT)


def get_national_id_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_NATIONAL_ID)


def get_other_id_issuer(individual: Individual) -> str | None:
    return get_document_issuer(individual, IDENTIFICATION_TYPE_OTHER)


def get_document_issuer(individual: Individual, document_type: str) -> str:
    if document := individual.documents.filter(type__key=document_type.lower()).first():
        return getattr(document.country, "iso_code3", "")
    return ""


def get_unhcr_id_no(individual: Individual) -> str:
    if identity := individual.identities.filter(partner__name=UNHCR).first():
        return identity.number
    return ""


def get_unhcr_id_issuer(individual: Individual) -> str:
    if identity := individual.identities.filter(partner__name=UNHCR).first():
        return getattr(identity.country, "iso_code3", "")
    return ""


def get_scope_id_no(individual: Individual) -> str:
    if identity := individual.identities.filter(partner__name=WFP).first():
        return identity.number
    return ""


def get_scope_id_issuer(individual: Individual) -> str:
    if identity := individual.identities.filter(partner__name=WFP).first():
        return getattr(identity.country, "iso_code3", "")
    return ""
