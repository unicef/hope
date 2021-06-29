import logging

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.household.models import RELATIONSHIP_UNKNOWN

logger = logging.getLogger(__name__)


def handle_role(role, household, individual):
    from hct_mis_api.apps.household.models import (
        ROLE_ALTERNATE,
        ROLE_PRIMARY,
        IndividualRoleInHousehold,
    )

    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        already_existing_role = IndividualRoleInHousehold.objects.filter(household=household, role=role).first()
        if already_existing_role:
            already_existing_role.individual = individual
            already_existing_role.save()
        else:
            IndividualRoleInHousehold.objects.create(individual=individual, household=household, role=role)


def handle_add_document(document, individual):
    from django_countries.fields import Country
    from graphql import GraphQLError

    from hct_mis_api.apps.household.models import Document, DocumentType

    type_name = document.get("type")
    country_code = document.get("country")
    country = Country(country_code)
    number = document.get("number")
    document_type = DocumentType.objects.get(country=country, type=type_name)

    document_already_exists = Document.objects.filter(document_number=number, type=document_type).exists()
    if document_already_exists:
        logger.error(f"Document with number {number} of type {type_name} for country {country} already exist")
        raise GraphQLError(f"Document with number {number} of type {type_name} for country {country} already exist")

    return Document(document_number=number, individual=individual, type=document_type)


def handle_add_identity(identity, individual):
    from django_countries.fields import Country
    from graphql import GraphQLError

    from hct_mis_api.apps.household.models import Agency, IndividualIdentity

    agency_name = identity.get("agency")
    country_code = identity.get("country")
    country = Country(country_code)
    number = identity.get("number")
    agency_type, _ = Agency.objects.get_or_create(
        country=country,
        type=agency_name,
        defaults={"country": country, "type": agency_name, "label": f"{country.name} - {agency_name}"},
    )

    identity_already_exists = IndividualIdentity.objects.filter(number=number, agency=agency_type).exists()
    if identity_already_exists:
        logger.error(f"Identity with number {number}, agency: {agency_name} already exist")
        raise GraphQLError(f"Identity with number {number}, agency: {agency_name} already exist")

    return IndividualIdentity(number=number, individual=individual, agency=agency_type)


def prepare_previous_documents(documents_to_remove_with_approve_status):
    from django.shortcuts import get_object_or_404

    from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64
    from hct_mis_api.apps.household.models import Document

    previous_documents = {}
    for document_data in documents_to_remove_with_approve_status:
        document_id = decode_id_string(document_data.get("value"))
        document = get_object_or_404(Document, id=document_id)
        previous_documents[encode_id_base64(document.id, "Document")] = {
            "id": encode_id_base64(document.id, "Document"),
            "document_number": document.document_number,
            "individual": encode_id_base64(document.individual.id, "Individual"),
            "label": document.type.label,
            "country": document.type.country.alpha3,
        }

    return previous_documents


def prepare_previous_identities(identities_to_remove_with_approve_status):
    from django.shortcuts import get_object_or_404

    from hct_mis_api.apps.core.utils import encode_id_base64
    from hct_mis_api.apps.household.models import IndividualIdentity

    previous_identities = {}
    for identity_data in identities_to_remove_with_approve_status:
        identity_id = identity_data.get("value")
        identity = get_object_or_404(IndividualIdentity, id=identity_id)
        previous_identities[identity.id] = {
            "id": identity.id,
            "number": identity.number,
            "individual": encode_id_base64(identity.individual.id, "Individual"),
            "label": identity.agency.label,
            "country": identity.agency.country.alpha3,
        }

    return previous_identities


def verify_required_arguments(input_data, field_name, options):
    from graphql import GraphQLError

    from hct_mis_api.apps.core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                logger.error(f"You have to provide {required} in {key}")
                raise GraphQLError(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                logger.error(f"You can't provide {not_allowed} in {key}")
                raise GraphQLError(f"You can't provide {not_allowed} in {key}")


def remove_parsed_data_fields(data_dict, fields_list):
    for field in fields_list:
        data_dict.pop(field, None)


def verify_flex_fields(flex_fields_to_verify, associated_with):
    from hct_mis_api.apps.core.core_fields_attributes import (
        FIELD_TYPES_TO_INTERNAL_TYPE,
        TYPE_SELECT_MANY,
        TYPE_SELECT_ONE,
    )
    from hct_mis_api.apps.core.utils import serialize_flex_attributes

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
        field_choices = set(f.get("value") for f in flex_field["choices"])
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


def withdraw_individual_and_reassign_roles(ticket_details, individual_to_remove, info):
    old_individual_to_remove, removed_individual_household = reassign_roles(individual_to_remove, info, ticket_details)
    withdraw_individual(individual_to_remove, info, old_individual_to_remove, removed_individual_household)


def mark_as_duplicate_individual_and_reassign_roles(ticket_details, individual_to_remove, info, unique_individual):
    old_individual_to_remove, removed_individual_household = reassign_roles(individual_to_remove, info, ticket_details)
    mark_as_duplicate_individual(
        individual_to_remove, info, old_individual_to_remove, removed_individual_household, unique_individual
    )


def get_data_from_role_data(role_data):
    from django.shortcuts import get_object_or_404

    from hct_mis_api.apps.core.utils import decode_id_string
    from hct_mis_api.apps.household.models import Household, Individual

    role_name = role_data.get("role")

    individual_id = decode_id_string(role_data.get("individual"))
    household_id = decode_id_string(role_data.get("household"))

    old_individual = get_object_or_404(Individual, id=individual_id)
    new_individual = get_object_or_404(Individual, id=individual_id)

    household = get_object_or_404(Household, id=household_id)
    return role_name, old_individual, new_individual, household


def reassign_roles(individual_to_remove, info, ticket_details):
    from django.shortcuts import get_object_or_404

    from graphql import GraphQLError

    from hct_mis_api.apps.household.models import (
        HEAD,
        ROLE_ALTERNATE,
        ROLE_PRIMARY,
        Individual,
        IndividualRoleInHousehold,
    )

    old_individual_to_remove = Individual.objects.get(id=individual_to_remove.id)
    roles_to_bulk_update = []
    for role_data in ticket_details.role_reassign_data.values():
        role_name, old_new_individual, new_individual, household = get_data_from_role_data(role_data)

        if role_name == HEAD:
            household.head_of_household = new_individual
            # can be directly saved, because there is always only one head of household to update
            household.save()
            household.individuals.exclude(id=new_individual.id).update(relationship=RELATIONSHIP_UNKNOWN)
            new_individual.relationship = HEAD
            new_individual.save()
            log_create(
                Individual.ACTIVITY_LOG_MAPPING,
                "business_area",
                info.context.user,
                old_new_individual,
                new_individual,
            )

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold, role=role_name, household=household, individual=individual_to_remove
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)
    household = individual_to_remove.household
    can_be_closed_because_of_empty_household = household.individuals.count() == 1 if household else False
    if len(roles_to_bulk_update) != individual_to_remove.count_all_roles() and not can_be_closed_because_of_empty_household:
        logger.error("Ticket cannot be closed, not all roles have been reassigned")
        raise GraphQLError("Ticket cannot be closed, not all roles have been reassigned")
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])
    removed_individual_household = individual_to_remove.household
    if removed_individual_household:
        removed_individual_is_head = removed_individual_household.head_of_household.id == individual_to_remove.id
    else:
        removed_individual_is_head = False
    if (
        not any(True if HEAD in key else False for key in ticket_details.role_reassign_data.keys())
        and removed_individual_is_head and not can_be_closed_because_of_empty_household
    ):
        logger.error("Ticket cannot be closed head of household has not been reassigned")
        raise GraphQLError("Ticket cannot be closed head of household has not been reassigned")
    return old_individual_to_remove, removed_individual_household


def reassign_roles_on_update(individual, role_reassign_data, info, should_log=True):
    from django.shortcuts import get_object_or_404

    from hct_mis_api.apps.household.models import (
        HEAD,
        ROLE_ALTERNATE,
        ROLE_PRIMARY,
        Individual,
        IndividualRoleInHousehold,
    )

    roles_to_bulk_update = []
    for role_data in role_reassign_data.values():
        role_name, old_new_individual, new_individual, household = get_data_from_role_data(role_data)

        if role_name == HEAD:
            household.head_of_household = new_individual
            household.save()
            new_individual.relationship = HEAD
            new_individual.save()
            if should_log:
                log_create(
                    Individual.ACTIVITY_LOG_MAPPING,
                    "business_area",
                    info.context.user,
                    old_new_individual,
                    new_individual,
                )

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold, role=role_name, household=household, individual=individual
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])


def withdraw_individual(individual_to_remove, info, old_individual_to_remove, removed_individual_household):
    individual_to_remove.withdraw()
    log_and_withdraw_household_if_needed(
        individual_to_remove, info, old_individual_to_remove, removed_individual_household
    )


def mark_as_duplicate_individual(
    individual_to_remove, info, old_individual_to_remove, removed_individual_household, unique_individual
):
    individual_to_remove.mark_as_duplicate(unique_individual)
    log_and_withdraw_household_if_needed(
        individual_to_remove, info, old_individual_to_remove, removed_individual_household
    )


def log_and_withdraw_household_if_needed(
    individual_to_remove, info, old_individual_to_remove, removed_individual_household
):
    from hct_mis_api.apps.household.models import Individual

    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        info.context.user,
        old_individual_to_remove,
        individual_to_remove,
    )
    if removed_individual_household:
        if removed_individual_household.individuals.count() == 0:
            removed_individual_household.withdraw()
        else:
            removed_individual_household.size -= 1
            removed_individual_household.save()
