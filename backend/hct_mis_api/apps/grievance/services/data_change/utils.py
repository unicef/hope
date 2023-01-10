import logging
import random
import string
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.core_fields_attributes import (
    FIELD_TYPES_TO_INTERNAL_TYPE,
    TYPE_IMAGE,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    encode_id_base64,
    encode_id_base64_required,
    serialize_flex_attributes,
)
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)

logger = logging.getLogger(__name__)


def to_date_string(data: Dict, field_name: str) -> None:
    if raw_date := data.get(field_name):
        data[field_name] = raw_date.isoformat()


def to_phone_number_str(data: Dict, field_name: str) -> None:
    if phone_number := data.get(field_name):
        data[field_name] = str(phone_number)


def is_approved(item: Dict) -> bool:
    return item.get("approve_status") is True


def convert_to_empty_string_if_null(value: Any) -> Union[Any, str]:
    return value or ""


def cast_flex_fields(flex_fields: Dict) -> None:
    decimals_flex_attrs_name_list = FlexibleAttribute.objects.filter(type="DECIMAL").values_list("name", flat=True)
    integer_flex_attrs_name_list = FlexibleAttribute.objects.filter(type="INTEGER").values_list("name", flat=True)
    for key, value in flex_fields.items():
        if key in decimals_flex_attrs_name_list:
            flex_fields[key] = float(value)
        if key in integer_flex_attrs_name_list:
            flex_fields[key] = int(value)


def verify_flex_fields(flex_fields_to_verify: Dict, associated_with: str) -> None:
    if associated_with not in ("households", "individuals"):
        logger.error("associated_with argument must be one of ['household', 'individual']")
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields_to_verify.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            logger.error(f"{name} is not a correct `flex field")
            raise ValueError(f"{name} is not a correct `flex field")
        field_type = flex_field["type"]
        field_choices = {f.get("value") for f in flex_field["choices"]}
        if not isinstance(value, FIELD_TYPES_TO_INTERNAL_TYPE[field_type]) or value is None:
            logger.error(f"invalid value type for a field {name}")
            raise ValueError(f"invalid value type for a field {name}")

        if field_type == TYPE_SELECT_ONE and value not in field_choices:
            logger.error(f"invalid value: {value} for a field {name}")
            raise ValueError(f"invalid value: {value} for a field {name}")

        if field_type == TYPE_SELECT_MANY:
            values = set(value)
            if values.issubset(field_choices) is False:
                logger.error(f"invalid value: {value} for a field {name}")
                raise ValueError(f"invalid value: {value} for a field {name}")


def handle_role(role: str, household: Household, individual: Individual) -> None:
    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        already_existing_role = IndividualRoleInHousehold.objects.filter(household=household, role=role).first()
        if already_existing_role:
            already_existing_role.individual = individual
            already_existing_role.save()
        else:
            IndividualRoleInHousehold.objects.create(individual=individual, household=household, role=role)


def handle_add_document(document: Dict, individual: Individual) -> Document:
    type_name = document.get("type")
    country_code = document.get("country")
    country = geo_models.Country.objects.get(iso_code3=country_code)
    number = document.get("number")
    photo = document.get("photo")
    photoraw = document.get("photoraw")
    if photo:
        photo = photoraw
    document_type = DocumentType.objects.get(type=type_name)

    document_already_exists = Document.objects.filter(
        document_number=number, type=document_type, country=country
    ).exists()
    if document_already_exists:
        raise ValidationError(f"Document with number {number} of type {type_name} already exists")

    return Document(document_number=number, individual=individual, type=document_type, photo=photo, country=country)


def handle_edit_document(document_data: Dict) -> Document:
    updated_document = document_data.get("value", {})

    type_name = updated_document.get("type")
    country_code = updated_document.get("country")
    country = geo_models.Country.objects.get(iso_code3=country_code)
    number = updated_document.get("number")
    photo = updated_document.get("photo")
    photoraw = updated_document.get("photoraw")
    if photo:
        photo = photoraw

    document_id = decode_id_string(updated_document.get("id"))
    document_type = DocumentType.objects.get(type=type_name)

    document_already_exists = (
        Document.objects.exclude(pk=document_id)
        .filter(document_number=number, type=document_type, country=country)
        .exists()
    )
    if document_already_exists:
        raise ValidationError(f"Document with number {number} of type {type_name} already exists")

    document = get_object_or_404(Document.objects.select_for_update(), id=document_id)

    document.document_number = number
    document.type = document_type
    document.country = country
    document.photo = photo

    return document


def handle_add_payment_channel(payment_channel: Dict, individual: Individual) -> Optional[BankAccountInfo]:
    payment_channel_type = payment_channel.get("type")
    if payment_channel_type == "BANK_TRANSFER":
        bank_name = payment_channel.get("bank_name")
        bank_account_number = payment_channel.get("bank_account_number")
        return BankAccountInfo(
            individual=individual,
            bank_name=bank_name,
            bank_account_number=bank_account_number,
        )
    return None


def handle_update_payment_channel(payment_channel: Dict) -> Optional[BankAccountInfo]:
    payment_channel_type = payment_channel.get("type")
    payment_channel_id = decode_id_string(payment_channel.get("id"))

    if payment_channel_type == "BANK_TRANSFER":
        bank_account_info = get_object_or_404(BankAccountInfo, id=payment_channel_id)
        bank_account_info.bank_name = payment_channel.get("bank_name")
        bank_account_info.bank_account_number = payment_channel.get("bank_account_number")
        return bank_account_info

    return None


def handle_add_identity(identity: Dict, individual: Individual) -> IndividualIdentity:
    partner_name = identity.get("partner")
    country_code = identity.get("country")
    country = geo_models.Country.objects.get(iso_code3=country_code)
    number = identity.get("number")
    partner, _ = Partner.objects.get_or_create(name=partner_name)

    identity_already_exists = IndividualIdentity.objects.filter(number=number, partner=partner).exists()
    if identity_already_exists:
        raise ValidationError(f"Identity with number {number}, partner: {partner_name} already exists")

    return IndividualIdentity(number=number, individual=individual, partner=partner, country=country)


def handle_edit_identity(identity_data: Dict) -> IndividualIdentity:
    updated_identity = identity_data.get("value", {})
    partner_name = updated_identity.get("partner")
    number = updated_identity.get("number")
    identity_id = updated_identity.get("id")
    country_code = updated_identity.get("country")

    country = geo_models.Country.objects.get(iso_code3=country_code)
    identity = get_object_or_404(IndividualIdentity, id=decode_id_string(identity_id))
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


def prepare_previous_documents(documents_to_remove_with_approve_status: List[Dict]) -> Dict[str, Dict]:
    previous_documents: Dict[str, Any] = {}
    for document_data in documents_to_remove_with_approve_status:
        document_id = decode_id_string(document_data.get("value"))
        document: Document = get_object_or_404(Document, id=document_id)
        previous_documents[encode_id_base64_required(document.id, "Document")] = {
            "id": encode_id_base64(document.id, "Document"),
            "document_number": document.document_number,
            "individual": encode_id_base64(document.individual.id, "Individual"),
            "type": document.type.type,
            "country": document.country.iso_code3,
        }

    return previous_documents


def prepare_previous_identities(identities_to_remove_with_approve_status: List[Dict]) -> Dict[int, Any]:
    previous_identities = {}
    for identity_data in identities_to_remove_with_approve_status:
        identity_id = identity_data.get("value")
        identity = get_object_or_404(IndividualIdentity, id=decode_id_string(identity_id))
        previous_identities[identity.id] = {
            "id": identity.id,
            "number": identity.number,
            "individual": encode_id_base64(identity.individual.id, "Individual"),
            "partner": identity.partner.name,
            "country": identity.country.iso_code3,
        }

    return previous_identities


def prepare_previous_payment_channels(payment_channels_to_remove_with_approve_status: List[Dict]) -> Dict[str, Any]:
    previous_payment_channels = {}
    for payment_channel_data in payment_channels_to_remove_with_approve_status:
        payment_channel_id: str = payment_channel_data.get("value", "")
        bank_account_info = get_object_or_404(BankAccountInfo, id=decode_id_string(payment_channel_id))
        previous_payment_channels[payment_channel_id] = {
            "id": payment_channel_id,
            "individual": encode_id_base64(bank_account_info.individual.id, "Individual"),
            "bank_name": bank_account_info.bank_name,
            "bank_account_number": bank_account_info.bank_account_number,
            "type": "BANK_TRANSFER",
        }

    return previous_payment_channels


def prepare_edit_identities(identities: List[Dict]) -> List[Dict]:
    edited_identities = []
    for identity_data in identities:
        encoded_id = identity_data.get("id")
        number = identity_data.get("number")
        partner = identity_data.get("partner")
        country = identity_data.get("country")

        identity_id = decode_id_string(encoded_id)
        identity = get_object_or_404(IndividualIdentity, id=identity_id)

        edited_identities.append(
            {
                "approve_status": False,
                "value": {
                    "id": encoded_id,
                    "country": country,
                    "partner": partner,
                    "individual": encode_id_base64(identity.individual.id, "Individual"),
                    "number": number,
                },
                "previous_value": {
                    "id": encoded_id,
                    "country": identity.country.iso_code3,
                    "partner": identity.partner.name,
                    "individual": encode_id_base64(identity.individual.id, "Individual"),
                    "number": identity.number,
                },
            }
        )
    return edited_identities


def prepare_edit_payment_channel(payment_channels: List[Dict]) -> List[Dict]:
    items = []

    handlers = {
        "BANK_TRANSFER": handle_bank_transfer_payment_method,
    }

    for pc in payment_channels:
        handler = handlers.get(pc.get("type"))  # type: ignore # FIXME: Argument 1 to "get" of "dict" has incompatible type "Optional[Any]"; expected "str"
        items.append(handler(pc))
    return items


def handle_bank_transfer_payment_method(pc: Dict) -> Dict:
    bank_account_number = pc.get("bank_account_number")
    bank_name = pc.get("bank_name")
    encoded_id = pc.get("id")
    payment_channel_type = pc.get("type")
    bank_account_info = get_object_or_404(BankAccountInfo, id=decode_id_string(encoded_id))
    return {
        "approve_status": False,
        "value": {
            "id": encoded_id,
            "individual": encode_id_base64(bank_account_info.individual.id, "Individual"),
            "bank_account_number": bank_account_number,
            "bank_name": bank_name,
            "type": payment_channel_type,
        },
        "previous_value": {
            "id": encoded_id,
            "individual": encode_id_base64(bank_account_info.individual.id, "Individual"),
            "bank_account_number": bank_account_info.bank_account_number,
            "bank_name": bank_account_info.bank_name,
            "type": payment_channel_type,
        },
    }


def generate_filename() -> str:
    file_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{file_name}-{timezone.now()}"


def handle_photo(photo: Union[InMemoryUploadedFile, str], photoraw: Optional[str]) -> Optional[str]:
    if isinstance(photo, InMemoryUploadedFile):
        return default_storage.save(f"{generate_filename()}.jpg", photo)
    elif isinstance(photo, str):
        return photoraw
    return None


def handle_document(document: Dict) -> Dict:
    photo = document.get("photo")
    photoraw = document.get("photoraw")
    document["photo"] = handle_photo(photo, photoraw)
    document["photoraw"] = document["photo"]
    return document


def handle_documents(documents: List[Dict]) -> List[Dict]:
    return [handle_document(document) for document in documents]


def save_images(flex_fields: Dict, associated_with: str) -> None:
    if associated_with not in ("households", "individuals"):
        logger.error("associated_with argument must be one of ['household', 'individual']")
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            logger.error(f"{name} is not a correct `flex field")
            raise ValueError(f"{name} is not a correct `flex field")

        if flex_field["type"] == TYPE_IMAGE:
            if isinstance(value, InMemoryUploadedFile):
                file_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
                flex_fields[name] = default_storage.save(f"{file_name}-{timezone.now()}.jpg", value)
            elif isinstance(value, str):
                file_name = value.replace(default_storage.base_url, "")
                unquoted_value = urllib.parse.unquote(file_name)
                flex_fields[name] = unquoted_value


def prepare_edit_documents(documents_to_edit: List[Dict]) -> List[Dict]:
    edited_documents = []

    for document_to_edit in documents_to_edit:
        encoded_id = document_to_edit.get("id")
        document_type = document_to_edit.get("type")
        country = document_to_edit.get("country")
        document_number = document_to_edit.get("number")
        document_photo = document_to_edit.get("photo")
        document_photoraw = document_to_edit.get("photoraw")

        document_photo = handle_photo(document_photo, document_photoraw)

        document_id = decode_id_string(encoded_id)
        document = get_object_or_404(Document, id=document_id)

        edited_documents.append(
            {
                "approve_status": False,
                "value": {
                    "id": encoded_id,
                    "type": document_type,
                    "country": country,
                    "number": document_number,
                    "photo": document_photo,
                    "photoraw": document_photo,
                },
                "previous_value": {
                    "id": encoded_id,
                    "type": document.type.type,
                    "country": document.country.iso_code3,
                    "number": document.document_number,
                    "photo": document.photo.name,
                    "photoraw": document.photo.name,
                },
            }
        )

    return edited_documents
