import logging
import random
import string
import urllib.parse
from collections import Counter
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, Union

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.field_attributes.fields_types import (
    FIELD_TYPES_TO_INTERNAL_TYPE,
    TYPE_DATE,
    TYPE_IMAGE,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import (
    encode_id_base64,
    encode_id_base64_required,
    serialize_flex_attributes,
)
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    HEAD,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Account, AccountType
from hct_mis_api.apps.utils.models import MergeStatusModel

if TYPE_CHECKING:
    from uuid import UUID

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
    return "" if value is None else value


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
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields_to_verify.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            raise ValueError(f"{name} is not a correct `flex field")
        field_type = flex_field["type"]
        field_choices = {f.get("value") for f in flex_field["choices"]}

        if field_type == TYPE_DATE:
            # convert string value to datetime
            value = datetime.strptime(value, "%Y-%m-%d")

        if not isinstance(value, FIELD_TYPES_TO_INTERNAL_TYPE[field_type]) or value is None:
            raise ValueError(f"invalid value type for a field {name}")

        if field_type == TYPE_SELECT_ONE and value not in field_choices:
            raise ValueError(f"invalid value: {value} for a field {name}")

        if field_type == TYPE_SELECT_MANY:
            values = set(value)
            if values.issubset(field_choices) is False:
                raise ValueError(f"invalid value: {value} for a field {name}")


def handle_role(role: str, household: Household, individual: Individual) -> None:
    if already_with_another_role := IndividualRoleInHousehold.objects.filter(
        household=household,
        individual=individual,
    ).first():
        if already_with_another_role.role == ROLE_PRIMARY:
            raise ValidationError("Ticket cannot be closed, primary collector role has to be reassigned")
        else:
            already_with_another_role.delete(soft=False)

    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        IndividualRoleInHousehold.objects.update_or_create(
            household=household,
            role=role,
            defaults={"individual": individual},
            rdi_merge_status=MergeStatusModel.MERGED,
        )


def handle_add_document(document_data: Dict, individual: Individual) -> Document:
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

    country = geo_models.Country.objects.get(iso_code3=country_code)

    return Document(
        document_number=number,
        individual=individual,
        type=document_type,
        photo=photo,
        country=country,
        program_id=individual.program_id,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


def handle_edit_document(document_data: Dict) -> Document:
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
    document.country = geo_models.Country.objects.get(iso_code3=country_code)
    document.photo = photo

    return document


def handle_add_identity(identity: Dict, individual: Individual) -> IndividualIdentity:
    partner_name = identity.get("partner")
    country_code = identity.get("country")
    country = geo_models.Country.objects.get(iso_code3=country_code)
    number = identity.get("number")
    partner, _ = Partner.objects.get_or_create(name=partner_name)

    identity_already_exists = IndividualIdentity.objects.filter(number=number, partner=partner).exists()
    if identity_already_exists:
        raise ValidationError(f"Identity with number {number}, partner: {partner_name} already exists")

    return IndividualIdentity(
        number=number, individual=individual, partner=partner, country=country, rdi_merge_status=MergeStatusModel.MERGED
    )


def handle_edit_identity(identity_data: Dict) -> IndividualIdentity:
    updated_identity = identity_data.get("value", {})
    partner_name = updated_identity.get("partner")
    number = updated_identity.get("number")
    identity_id = updated_identity.get("id")
    country_code = updated_identity.get("country")

    country = geo_models.Country.objects.get(iso_code3=country_code)
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


def prepare_edit_accounts_save(accounts: List[Dict]) -> List[Dict]:
    items = []
    for account in accounts:
        _id = account.pop("id")
        delivery_mechanism_data = get_object_or_404(Account, id=_id)
        data = {
            "id": _id,
            "name": delivery_mechanism_data.account_type.key,
            "approve_status": False,
            "data_fields": [
                {
                    "name": field,
                    "value": value,
                    "previous_value": delivery_mechanism_data.account_data.get(field),
                }
                for field, value in account["data_fields"].items()
            ],
        }
        items.append(data)
    return items


def handle_update_account(account: Dict) -> Optional[Account]:
    account_instance = get_object_or_404(Account, id=account.get("id"))
    data_fields_dict = {field["name"]: field["value"] for field in account["data_fields"]}
    account_instance.account_data = data_fields_dict
    return account_instance


def handle_add_account(account: Dict, individual: Individual) -> Account:
    account_instance = Account(
        individual=individual,
        account_type=AccountType.objects.get(key=account["name"]),
        rdi_merge_status=individual.rdi_merge_status,
    )
    account_instance.account_data = account["data_fields"]
    return account_instance


def prepare_previous_documents(documents_to_remove_with_approve_status: List[Dict]) -> Dict[str, Dict]:
    previous_documents: Dict[str, Any] = {}
    for document_data in documents_to_remove_with_approve_status:
        document_id = document_data.get("value")
        document: Document = get_object_or_404(Document, id=document_id)
        previous_documents[encode_id_base64_required(document.id, "Document")] = {
            "id": encode_id_base64(document.id, "Document"),
            "document_number": document.document_number,
            "individual": encode_id_base64(document.individual.id, "Individual"),
            "key": document.type.key,
            "country": document.country.iso_code3,
        }

    return previous_documents


def prepare_edit_documents(documents_to_edit: List[Document]) -> List[Dict]:
    edited_documents = []

    for document_to_edit in documents_to_edit:
        document = document_to_edit.get("id")
        document_key = document_to_edit.get("key")
        country = document_to_edit.get("country")
        document_number = document_to_edit.get("number")
        document_photo = document_to_edit.get("photo")
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


def prepare_previous_identities(identities_to_remove_with_approve_status: List[Dict]) -> Dict[str, Any]:
    previous_identities: Dict[str, Any] = {}
    for identity_data in identities_to_remove_with_approve_status:
        identity_id = identity_data.get("value")
        identity = get_object_or_404(IndividualIdentity, id=identity_id)
        encoded_identity = encode_id_base64_required(identity.id, "IndividualIdentity")
        previous_identities[encoded_identity] = {
            "id": encoded_identity,  # TODO: can be removed maybe
            "number": identity.number,
            "individual": encode_id_base64(identity.individual.id, "Individual"),
            "partner": identity.partner.name,
            "country": identity.country.iso_code3,
        }

    return previous_identities


def prepare_edit_identities(identities: List[Dict]) -> List[Dict]:
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
    file_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{file_name}-{timezone.now()}"


def handle_photo(photo: Optional[Union[InMemoryUploadedFile, str]], photoraw: Optional[str]) -> Optional[str]:
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


def verify_required_arguments(input_data: Dict, field_name: str, options: Dict) -> None:
    from hct_mis_api.apps.core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                raise ValidationError(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                raise ValidationError(f"You can't provide {not_allowed} in {key}")


def remove_parsed_data_fields(data_dict: Dict, fields_list: Iterable[str]) -> None:
    for field in fields_list:
        data_dict.pop(field, None)


def withdraw_individual_and_reassign_roles(ticket_details: Any, individual_to_remove: Individual, info: Any) -> None:
    old_individual = Individual.objects.get(id=individual_to_remove.id)
    household = reassign_roles_on_disable_individual(
        individual_to_remove,
        ticket_details.role_reassign_data,
        ticket_details.programs.all(),
        info,
    )
    withdraw_individual(individual_to_remove, info, old_individual, household, ticket_details.ticket.programs.all())


def get_data_from_role_data(role_data: Dict) -> Tuple[Optional[Any], Individual, Individual, Household]:
    role_name = role_data.get("role")

    individual_id = role_data.get("individual")
    household_id = role_data.get("household")

    old_individual = get_object_or_404(Individual, id=individual_id)
    new_individual = get_object_or_404(Individual, id=individual_id)

    household = get_object_or_404(Household, id=household_id)
    return role_name, old_individual, new_individual, household


def get_data_from_role_data_new_ticket(role_data: Dict) -> Tuple[Optional[Any], Individual, Individual, Household]:
    role_name, old_individual, _, household = get_data_from_role_data(role_data)
    new_individual_id = role_data.get("new_individual")
    new_individual = get_object_or_404(Individual, id=new_individual_id)

    return role_name, old_individual, new_individual, household


def reassign_roles_on_disable_individual(
    individual_to_remove: Individual,
    role_reassign_data: Dict,
    program_id: Optional["UUID"],
    info: Optional[Any] = None,
    is_new_ticket: bool = False,
) -> Optional[Household]:
    roles_to_bulk_update = []
    roles_to_delete = []
    for role_data in role_reassign_data.values():
        if is_new_ticket:
            (
                role_name,
                old_new_individual,
                new_individual,
                household,
            ) = get_data_from_role_data_new_ticket(role_data)
        else:
            (
                role_name,
                old_new_individual,
                new_individual,
                household,
            ) = get_data_from_role_data(role_data)

        if role_name == HEAD:
            if household.head_of_household.pk != new_individual.pk:
                household.head_of_household = new_individual

                # can be directly saved, because there is always only one head of household to update
                household.save()
                household.individuals.exclude(id=new_individual.id).update(relationship=RELATIONSHIP_UNKNOWN)
            new_individual.relationship = HEAD
            new_individual.save()
            if info:
                log_create(
                    Individual.ACTIVITY_LOG_MAPPING,
                    "business_area",
                    info.context.user,
                    program_id,
                    old_new_individual,
                    new_individual,
                )

        if new_individual_current_role := IndividualRoleInHousehold.objects.filter(
            household=household, individual=new_individual
        ).first():
            if role_name == ROLE_ALTERNATE and new_individual_current_role.role == ROLE_PRIMARY:
                raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")
            elif (
                role_name == ROLE_PRIMARY and new_individual_current_role.role == ROLE_ALTERNATE
            ):  # remove alternate role if the new individual is being assigned as primary
                roles_to_delete.append(new_individual_current_role)

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold,
                role=role_name,
                household=household,
                individual=individual_to_remove,
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    primary_roles_count = Counter([role.get("role") for role in role_reassign_data.values()])[ROLE_PRIMARY]

    household_to_remove = individual_to_remove.household
    is_one_individual = household_to_remove.individuals.count() == 1 if household_to_remove else False

    if primary_roles_count != individual_to_remove.count_primary_roles() and not is_one_individual:
        raise ValidationError("Ticket cannot be closed, not all roles have been reassigned")

    if (
        all(HEAD not in key for key in role_reassign_data.keys())
        and individual_to_remove.is_head()
        and not is_one_individual
    ):
        raise ValidationError("Ticket cannot be closed, head of household has not been reassigned")

    for role_to_delete in roles_to_delete:
        role_to_delete.delete(soft=False)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])

    return household_to_remove


def reassign_roles_on_update(
    individual: Individual, role_reassign_data: Dict, program_id: "UUID", info: Optional[Any] = None
) -> None:
    roles_to_bulk_update = []
    roles_to_delete = []
    for role_data in role_reassign_data.values():
        (
            role_name,
            old_new_individual,
            new_individual,
            household,
        ) = get_data_from_role_data(role_data)

        if role_name == HEAD:
            household.head_of_household = new_individual
            household.save()
            new_individual.relationship = HEAD
            new_individual.save()
            if info:
                log_create(
                    Individual.ACTIVITY_LOG_MAPPING,
                    "business_area",
                    info.context.user,
                    program_id,
                    old_new_individual,
                    new_individual,
                )

        if new_individual_current_role := IndividualRoleInHousehold.objects.filter(
            household=household, individual=new_individual
        ).first():
            if role_name == ROLE_ALTERNATE and new_individual_current_role.role == ROLE_PRIMARY:
                raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")
            elif (
                role_name == ROLE_PRIMARY and new_individual_current_role.role == ROLE_ALTERNATE
            ):  # remove alternate role if the new individual is being assigned as primary
                roles_to_delete.append(new_individual_current_role)

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold,
                role=role_name,
                household=household,
                individual=individual,
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    for role_to_delete in roles_to_delete:
        role_to_delete.delete(soft=False)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])


def withdraw_individual(
    individual_to_remove: Individual,
    info: Any,
    old_individual_to_remove: Individual,
    removed_individual_household: Optional[Household],
    program_id: Optional["UUID"],
) -> None:
    individual_to_remove.withdraw()

    Document.objects.filter(status=Document.STATUS_VALID, individual=individual_to_remove).update(
        status=Document.STATUS_NEED_INVESTIGATION
    )
    log_and_withdraw_household_if_needed(
        individual_to_remove,
        info,
        old_individual_to_remove,
        removed_individual_household,
        program_id,
    )


def mark_as_duplicate_individual(
    individual_to_remove: Individual,
    info: Any,
    old_individual_to_remove: Individual,
    removed_individual_household: Optional[Household],
    unique_individual: Individual,
    program_id: Optional["UUID"],
) -> None:
    individual_to_remove.mark_as_duplicate(unique_individual)
    log_and_withdraw_household_if_needed(
        individual_to_remove, info, old_individual_to_remove, removed_individual_household, program_id
    )


def log_and_withdraw_household_if_needed(
    individual_to_remove: Individual,
    info: Any,
    old_individual_to_remove: Individual,
    removed_individual_household: Optional[Household],
    program_id: Optional["UUID"],
) -> None:
    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        info.context.user,
        program_id,
        old_individual_to_remove,
        individual_to_remove,
    )
    if removed_individual_household:
        removed_individual_household.refresh_from_db()
        if removed_individual_household.active_individuals.count() == 0:
            removed_individual_household.withdraw()


def save_images(flex_fields: Dict, associated_with: str) -> None:
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
                file_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
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
