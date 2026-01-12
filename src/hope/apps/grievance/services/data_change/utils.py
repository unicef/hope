from datetime import datetime
import logging
import secrets
import string
from typing import Any
import urllib.parse

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.core.field_attributes.fields_types import (
    FIELD_TYPES_TO_INTERNAL_TYPE,
    TYPE_DATE,
    TYPE_IMAGE,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
)
from hope.apps.core.utils import (
    serialize_flex_attributes,
)
from hope.apps.household.const import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hope.apps.household.documents import HouseholdDocument, get_individual_doc
from hope.models import (
    Account,
    AccountType,
    Country,
    Document,
    DocumentType,
    FlexibleAttribute,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Partner,
)
from hope.models.utils import MergeStatusModel

logger = logging.getLogger(__name__)


def to_date_string(data: dict, field_name: str) -> None:
    if raw_date := data.get(field_name):
        data[field_name] = raw_date.isoformat()


def to_phone_number_str(data: dict, field_name: str) -> None:
    if phone_number := data.get(field_name):
        data[field_name] = str(phone_number)


def is_approved(item: dict) -> bool:
    return item.get("approve_status") in [True, "true", "True"]


def convert_to_empty_string_if_null(value: Any) -> Any | str:
    return "" if value is None else value


def cast_flex_fields(flex_fields: dict) -> None:
    decimals_flex_attrs_name_list = FlexibleAttribute.objects.filter(type="DECIMAL").values_list("name", flat=True)
    integer_flex_attrs_name_list = FlexibleAttribute.objects.filter(type="INTEGER").values_list("name", flat=True)
    for key, value in flex_fields.items():
        if key in decimals_flex_attrs_name_list:
            flex_fields[key] = float(value)
        if key in integer_flex_attrs_name_list:
            flex_fields[key] = int(value)


def verify_flex_fields(flex_fields_to_verify: dict, associated_with: str) -> None:
    if associated_with not in ("households", "individuals"):
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, _value in flex_fields_to_verify.items():
        value = _value
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            raise ValueError(f"{name} is not a correct `flex field")
        field_type = flex_field["type"]
        field_choices = {f.get("value") for f in flex_field["choices"]}

        if field_type == TYPE_DATE:
            # convert string value to datetime
            value = datetime.strptime(value, "%Y-%m-%d")

        expected_type = FIELD_TYPES_TO_INTERNAL_TYPE[field_type]
        # handle integers passed as strings
        if expected_type is int and isinstance(value, str) and value.isdigit():
            value = int(value)

        if not isinstance(value, expected_type) or value is None:
            raise ValueError(f"invalid value type for a field {name}")

        if field_type == TYPE_SELECT_ONE and value not in field_choices:
            raise ValueError(f"invalid value: {value} for a field {name}")

        if field_type == TYPE_SELECT_MANY:
            values = set(value)
            if values.issubset(field_choices) is False:
                raise ValueError(f"invalid value: {value} for a field {name}")


def handle_role(household: Household, individual: Individual, role: str | None) -> None:
    if already_with_another_role := IndividualRoleInHousehold.objects.filter(
        household=household,
        individual=individual,
    ).first():
        if already_with_another_role.role == ROLE_PRIMARY:
            raise ValidationError("Ticket cannot be closed, primary collector role has to be reassigned")
        already_with_another_role.delete(soft=False)

    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        IndividualRoleInHousehold.objects.update_or_create(
            household=household,
            role=role,
            defaults={"individual": individual},
            rdi_merge_status=MergeStatusModel.MERGED,
        )


def handle_add_document(document_data: dict, individual: Individual) -> Document:
    document_key = document_data.get("key")
    country_code = document_data.get("country")
    number = document_data.get("number")
    photo = document_data.get("photo")
    photoraw = document_data.get("photoraw")
    if photo:
        photo = photoraw

    document_type = DocumentType.objects.get(key=document_key)

    if Document.objects.filter(
        document_number=number,
        type__key=document_key,
        country__iso_code3=country_code,
        program_id=individual.program_id,
        status=Document.STATUS_VALID,
    ).exists():
        raise ValidationError(f"Document with number {number} of type {document_type} already exists")

    if (
        document_type.unique_for_individual
        and Document.objects.filter(
            type__key=document_key,
            individual=individual,
            country__iso_code3=country_code,
            program_id=individual.program_id,
            status=Document.STATUS_VALID,
        ).exists()
    ):
        raise ValidationError(f"Document of type {document_type} already exists for this individual")

    country = Country.objects.get(iso_code3=country_code)

    return Document(
        document_number=number,
        individual=individual,
        type=document_type,
        photo=photo,
        country=country,
        program_id=individual.program_id,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


def handle_edit_document(document_data: dict) -> Document:
    document_key = document_data.get("key")
    country_code = document_data.get("country")
    number = document_data.get("number")
    photo = document_data.get("photo")
    photoraw = document_data.get("photoraw")
    if photo:
        photo = photoraw

    document = get_object_or_404(Document.objects.select_for_update(), id=(document_data.get("id")))
    document_type = DocumentType.objects.get(key=document_key)

    if (
        Document.objects.exclude(pk=document.id)
        .filter(
            document_number=number,
            type__key=document_key,
            country__iso_code3=country_code,
            program_id=document.program_id,
            status=Document.STATUS_VALID,
        )
        .exists()
    ):
        raise ValidationError(f"Document with number {number} of type {document_type} already exists")

    if (
        document_type.unique_for_individual
        and Document.objects.exclude(pk=document.id)
        .filter(
            type__key=document_key,
            individual=document.individual,
            country__iso_code3=country_code,
            program_id=document.program_id,
            status=Document.STATUS_VALID,
        )
        .exists()
    ):
        raise ValidationError(f"Document of type {document_type} already exists for this individual")

    document.document_number = number
    document.type = document_type
    document.country = Country.objects.get(iso_code3=country_code)
    document.photo = photo

    return document


def handle_add_identity(identity: dict, individual: Individual) -> IndividualIdentity:
    partner_name = identity.get("partner")
    country_code = identity.get("country")
    country = Country.objects.get(iso_code3=country_code)
    number = identity.get("number")
    partner, _ = Partner.objects.get_or_create(name=partner_name)

    identity_already_exists = IndividualIdentity.objects.filter(number=number, partner=partner).exists()
    if identity_already_exists:
        raise ValidationError(f"Identity with number {number}, partner: {partner_name} already exists")

    return IndividualIdentity(
        number=number,
        individual=individual,
        partner=partner,
        country=country,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


def handle_edit_identity(identity_data: dict) -> IndividualIdentity:
    updated_identity = identity_data.get("value", {})
    partner_name = updated_identity.get("partner")
    number = updated_identity.get("number")
    identity_id = updated_identity.get("id")
    country_code = updated_identity.get("country")

    country = Country.objects.get(iso_code3=country_code)  # pragma: no cover
    identity = get_object_or_404(IndividualIdentity, id=identity_id)
    partner, _ = Partner.objects.get_or_create(name=partner_name)

    identity_already_exists = (
        IndividualIdentity.objects.exclude(pk=identity.id).filter(number=number, partner=partner).exists()
    )
    if identity_already_exists:
        raise ValidationError(f"Identity with number {number}, partner: {partner_name} already exists")

    identity.number = number
    identity.partner = partner
    identity.country = country
    return identity


def prepare_edit_accounts_save(accounts: list[dict]) -> list[dict]:
    items = []
    for account in accounts:
        _id = account.pop("id")
        account_object = get_object_or_404(Account, id=_id)
        data_fields = account.get("data_fields", {})
        financial_institution = account.get("financial_institution")
        number = account.get("number")
        data = {
            "id": str(_id),
            "account_type": account_object.account_type.key,
            "approve_status": False,
            "financial_institution": financial_institution,
            "financial_institution_previous_value": account_object.financial_institution
            and account_object.financial_institution.pk,
            "number": number,
            "number_previous_value": account_object.number,
            "data_fields": [
                {
                    "name": item["key"],
                    "value": item["value"],
                    "previous_value": account_object.data.get(item["key"]),
                }
                for item in data_fields
            ],
        }
        items.append(data)
    return items


def handle_update_account(account: dict) -> Account | None:
    account_instance = get_object_or_404(Account, id=account.get("id"))
    data_fields_dict = {field["name"]: field["value"] for field in account["data_fields"]}
    account_instance.number = account["number"]
    account_instance.financial_institution_id = account.get("financial_institution")
    account_instance.account_data = data_fields_dict
    return account_instance


def handle_add_account(account: dict, individual: Individual) -> Account:
    account_instance = Account(
        individual=individual,
        account_type=AccountType.objects.get(key=account["account_type"]),
        financial_institution_id=account.get("financial_institution"),
        number=account["number"],
        rdi_merge_status=individual.rdi_merge_status,
    )
    account_instance.data = {item["key"]: item["value"] for item in account.get("data_fields", [])}
    return account_instance


def prepare_previous_documents(
    documents_to_remove_with_approve_status: list[dict],
) -> dict[str, dict]:
    previous_documents: dict[str, Any] = {}
    for document_data in documents_to_remove_with_approve_status:
        document_id = document_data.get("value")
        document: Document = get_object_or_404(Document, id=document_id)
        previous_documents[str(document.id)] = {
            "id": str(document.id),
            "document_number": document.document_number,
            "individual": str(document.individual.id),
            "key": document.type.key,
            "country": document.country.iso_code3,
        }

    return previous_documents


def prepare_edit_documents(documents_to_edit: list[Document]) -> list[dict]:
    edited_documents = []

    for document_to_edit in documents_to_edit:
        document = document_to_edit.get("id")
        document_key = document_to_edit.get("key")
        country = document_to_edit.get("country")
        document_number = document_to_edit.get("number")
        document_photo = document_to_edit.get("new_photo")
        document_photoraw = document_to_edit.get("photoraw")

        document_photo = handle_photo(document_photo, document_photoraw)

        document_id = str(document.id)

        edited_documents.append(
            {
                "approve_status": False,
                "value": {
                    "id": document_id,
                    "key": document_key,
                    "country": country,
                    "number": document_number,
                    "photo": document_photo,
                    "photoraw": document_photo,
                },
                "previous_value": {
                    "id": document_id,
                    "key": document.type.key,
                    "country": document.country.iso_code3,
                    "number": document.document_number,
                    "photo": document.photo.name,
                    "photoraw": document.photo.name,
                },
            }
        )

    return edited_documents


def prepare_previous_identities(
    identities_to_remove_with_approve_status: list[dict],
) -> dict[str, Any]:
    previous_identities: dict[str, Any] = {}
    for identity_data in identities_to_remove_with_approve_status:
        identity_id = identity_data.get("value")
        identity = get_object_or_404(IndividualIdentity, id=identity_id)
        previous_identities[str(identity.id)] = {
            "id": str(identity.id),
            "number": identity.number,
            "individual": str(identity.individual.id),
            "partner": identity.partner.name,
            "country": identity.country.iso_code3,
        }

    return previous_identities


def prepare_edit_identities(identities: list[dict]) -> list[dict]:
    edited_identities = []
    for identity_data in identities:
        identity = identity_data.get("id")
        number = identity_data.get("number")
        partner = identity_data.get("partner")
        country = identity_data.get("country")

        identity_id = str(identity.id)

        edited_identities.append(
            {
                "approve_status": False,
                "value": {
                    "id": identity_id,
                    "country": country,
                    "partner": partner,
                    "individual": str(identity.individual.id),
                    "number": number,
                },
                "previous_value": {
                    "id": identity_id,
                    "country": identity.country.iso_code3,
                    "partner": identity.partner.name,
                    "individual": str(identity.individual.id),
                    "number": identity.number,
                },
            }
        )
    return edited_identities


def generate_filename() -> str:
    file_name = "".join(secrets.choice(string.ascii_uppercase + string.digits))
    return f"{file_name}-{timezone.now()}"


def handle_photo(photo: InMemoryUploadedFile | str | None, photoraw: str | None) -> str | None:
    if isinstance(photo, InMemoryUploadedFile):
        photo = default_storage.save(f"{generate_filename()}.jpg", photo)
        return default_storage.url(photo)
    if isinstance(photo, str):
        return photoraw
    return None


def handle_document(document: dict) -> dict:
    photo = document.pop("new_photo") or document.get("photo")
    photoraw = document.get("photoraw")
    document["photo"] = handle_photo(photo, photoraw)
    document["photoraw"] = document["photo"]
    return document


def handle_documents(documents: list[dict]) -> list[dict]:
    return [handle_document(document) for document in documents]


def get_data_from_role_data(
    role_data: dict,
) -> tuple[Any | None, Individual, Individual, Household]:
    role_name = role_data.get("role")

    individual_id = role_data.get("individual")
    household_id = role_data.get("household")

    old_individual = get_object_or_404(Individual, id=individual_id)
    new_individual = get_object_or_404(Individual, id=individual_id)

    household = get_object_or_404(Household, id=household_id)
    return role_name, old_individual, new_individual, household


def save_images(flex_fields: dict, associated_with: str) -> None:
    if associated_with not in ("households", "individuals"):
        logger.warning("associated_with argument must be one of ['household', 'individual']")
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            logger.warning(f"{name} is not a correct `flex field")
            raise ValueError(f"{name} is not a correct `flex field")

        if flex_field["type"] == TYPE_IMAGE:
            if isinstance(value, InMemoryUploadedFile):
                file_name = "".join(secrets.choice(string.ascii_uppercase + string.digits))
                flex_fields[name] = default_storage.save(f"{file_name}-{timezone.now()}.jpg", value)
            elif isinstance(value, str):
                file_name = value.replace(default_storage.base_url, "")
                unquoted_value = urllib.parse.unquote(file_name)
                flex_fields[name] = unquoted_value


def update_es(individual: Individual) -> None:
    doc = get_individual_doc(individual.business_area.slug)
    doc().update(individual)
    if individual.household:
        HouseholdDocument().update(individual.household)
