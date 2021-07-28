from datetime import date, datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

import graphene
from django_countries.fields import Country
from graphql import GraphQLError

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import decode_id_string, to_snake_case
from hct_mis_api.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.grievance.mutations_extras.utils import (
    handle_add_document,
    handle_add_identity,
    handle_role,
    prepare_previous_documents,
    prepare_previous_identities,
    reassign_roles_on_update,
    verify_flex_fields,
    withdraw_individual_and_reassign_roles,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_NO_ROLE,
    Document,
    Household,
    Individual,
    IndividualIdentity,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.utils.schema import Arg


class HouseholdUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    consent = graphene.Boolean()
    consent_sharing = graphene.List(graphene.String)
    residence_status = graphene.String()
    country_origin = graphene.String()
    country = graphene.String()
    size = graphene.Int()
    address = graphene.String()
    female_age_group_0_5_count = graphene.Int()
    female_age_group_6_11_count = graphene.Int()
    female_age_group_12_17_count = graphene.Int()
    female_age_group_18_59_count = graphene.Int()
    female_age_group_60_count = graphene.Int()
    pregnant_count = graphene.Int()
    male_age_group_0_5_count = graphene.Int()
    male_age_group_6_11_count = graphene.Int()
    male_age_group_12_17_count = graphene.Int()
    male_age_group_18_59_count = graphene.Int()
    male_age_group_60_count = graphene.Int()
    female_age_group_0_5_disabled_count = graphene.Int()
    female_age_group_6_11_disabled_count = graphene.Int()
    female_age_group_12_17_disabled_count = graphene.Int()
    female_age_group_18_59_disabled_count = graphene.Int()
    female_age_group_60_disabled_count = graphene.Int()
    male_age_group_0_5_disabled_count = graphene.Int()
    male_age_group_6_11_disabled_count = graphene.Int()
    male_age_group_12_17_disabled_count = graphene.Int()
    male_age_group_18_59_disabled_count = graphene.Int()
    male_age_group_60_disabled_count = graphene.Int()
    returnee = graphene.Boolean()
    fchild_hoh = graphene.Boolean()
    child_hoh = graphene.Boolean()
    start = graphene.DateTime()
    end = graphene.DateTime()
    name_enumerator = graphene.String()
    org_enumerator = graphene.String()
    org_name_enumerator = graphene.String()
    village = graphene.String()
    registration_method = graphene.String()
    collect_individual_data = graphene.String()
    currency = graphene.String()
    unhcr_id = graphene.String()
    flex_fields = Arg()


class IndividualDocumentObjectType(graphene.InputObjectType):
    country = graphene.String(required=True)
    type = graphene.String(required=True)
    number = graphene.String(required=True)


class IndividualIdentityObjectType(graphene.InputObjectType):
    country = graphene.String(required=True)
    agency = graphene.String(required=True)
    number = graphene.String(required=True)


class IndividualUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    full_name = graphene.String()
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String()
    birth_date = graphene.Date()
    estimated_birth_date = graphene.Boolean()
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String()
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String()
    documents = graphene.List(IndividualDocumentObjectType)
    documents_to_remove = graphene.List(graphene.ID)
    identities = graphene.List(IndividualIdentityObjectType)
    identities_to_remove = graphene.List(graphene.ID)
    flex_fields = Arg()


class AddIndividualDataObjectType(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String(required=True)
    birth_date = graphene.Date(required=True)
    estimated_birth_date = graphene.Boolean(required=True)
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String(required=True)
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String(required=True)
    documents = graphene.List(IndividualDocumentObjectType)
    identities = graphene.List(IndividualIdentityObjectType)
    business_area = graphene.String()
    flex_fields = Arg()


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    household_data = HouseholdUpdateDataObjectType(required=True)


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    individual_data = IndividualUpdateDataObjectType(required=True)


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    individual_data = AddIndividualDataObjectType(required=True)


class UpdateHouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household_data = HouseholdUpdateDataObjectType(required=True)


class UpdateIndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual_data = IndividualUpdateDataObjectType(required=True)


class UpdateAddIndividualIssueTypeExtras(graphene.InputObjectType):
    individual_data = AddIndividualDataObjectType(required=True)


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)


def to_date_string(dict, field_name):
    date = dict.get(field_name)
    if date:
        dict[field_name] = date.isoformat()


def to_phone_number_str(dict, field_name):
    phone_number = dict.get(field_name)
    if phone_number:
        dict[field_name] = str(phone_number)


def save_data_change_extras(root, info, input, grievance_ticket, extras, **kwargs):
    issue_type = input.get("issue_type")
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL:
        return save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL:
        return save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE:
        return save_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)


def update_data_change_extras(root, info, input, grievance_ticket, extras, **kwargs):
    issue_type = grievance_ticket.issue_type
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return update_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL:
        return update_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs)
    if issue_type == GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE:
        return update_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)


def save_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    household_data_update_issue_type_extras = data_change_extras.get("household_data_update_issue_type_extras")

    household_encoded_id = household_data_update_issue_type_extras.get("household")
    household_id = decode_id_string(household_encoded_id)
    household = get_object_or_404(Household, id=household_id)
    household_data = household_data_update_issue_type_extras.get("household_data", {})
    to_date_string(household_data, "start")
    to_date_string(household_data, "end")
    flex_fields = {to_snake_case(field): value for field, value in household_data.pop("flex_fields", {}).items()}
    verify_flex_fields(flex_fields, "households")
    household_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in household_data.items()
    }

    for field, field_data in household_data_with_approve_status.items():
        current_value = getattr(household, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        if isinstance(current_value, Country):
            current_value = current_value.alpha3
        household_data_with_approve_status[field]["previous_value"] = current_value

    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
    ticket_individual_data_update_details = TicketHouseholdDataUpdateDetails(
        household_data=household_data_with_approve_status,
        household=household,
        ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_household_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.household_data_update_ticket_details
    household_data_update_new_extras = extras.get("household_data_update_issue_type_extras")
    household = ticket_details.household
    new_household_data = household_data_update_new_extras.get("household_data", {})
    to_date_string(new_household_data, "start")
    to_date_string(new_household_data, "end")
    flex_fields = {to_snake_case(field): value for field, value in new_household_data.pop("flex_fields", {}).items()}
    verify_flex_fields(flex_fields, "households")
    household_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in new_household_data.items()
    }

    for field, field_data in household_data_with_approve_status.items():
        current_value = getattr(household, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        if isinstance(current_value, Country):
            current_value = current_value.alpha3
        household_data_with_approve_status[field]["previous_value"] = current_value
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
    ticket_details.household_data = household_data_with_approve_status
    ticket_details.save()
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    individual_data_update_issue_type_extras = data_change_extras.get("individual_data_update_issue_type_extras")

    individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
    individual_id = decode_id_string(individual_encoded_id)
    individual = get_object_or_404(Individual, id=individual_id)
    individual_data = individual_data_update_issue_type_extras.get("individual_data", {})
    documents = individual_data.pop("documents", [])
    documents_to_remove = individual_data.pop("documents_to_remove", [])
    identities = individual_data.pop("identities", [])
    identities_to_remove = individual_data.pop("identities_to_remove", [])
    to_phone_number_str(individual_data, "phone_no")
    to_phone_number_str(individual_data, "phone_no_alternative")
    to_date_string(individual_data, "birth_date")
    flex_fields = {to_snake_case(field): value for field, value in individual_data.pop("flex_fields", {}).items()}
    verify_flex_fields(flex_fields, "individuals")
    individual_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in individual_data.items()
    }

    for field, field_data in individual_data_with_approve_status.items():
        current_value = getattr(individual, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        elif field in ("phone_no", "phone_no_alternative"):
            current_value = str(current_value)
        individual_data_with_approve_status[field]["previous_value"] = current_value

    documents_with_approve_status = [{"value": document, "approve_status": False} for document in documents]
    documents_to_remove_with_approve_status = [
        {"value": document_id, "approve_status": False} for document_id in documents_to_remove
    ]
    identities_with_approve_status = [{"value": identity, "approve_status": False} for identity in identities]
    identities_to_remove_with_approve_status = [
        {"value": identity_id, "approve_status": False} for identity_id in identities_to_remove
    ]
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    individual_data_with_approve_status["documents"] = documents_with_approve_status
    individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
    individual_data_with_approve_status["identities"] = identities_with_approve_status
    individual_data_with_approve_status["identities_to_remove"] = identities_to_remove_with_approve_status
    individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status

    individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
        documents_to_remove_with_approve_status
    )
    individual_data_with_approve_status["previous_identities"] = prepare_previous_identities(
        identities_to_remove_with_approve_status
    )
    ticket_individual_data_update_details = TicketIndividualDataUpdateDetails(
        individual_data=individual_data_with_approve_status,
        individual=individual,
        ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.individual_data_update_ticket_details

    individual_data_update_extras = extras.get("individual_data_update_issue_type_extras")

    individual = ticket_details.individual
    new_individual_data = individual_data_update_extras.get("individual_data", {})
    documents = new_individual_data.pop("documents", [])
    documents_to_remove = new_individual_data.pop("documents_to_remove", [])
    identities = new_individual_data.pop("identities", [])
    identities_to_remove = new_individual_data.pop("identities_to_remove", [])
    flex_fields = {to_snake_case(field): value for field, value in new_individual_data.pop("flex_fields", {}).items()}

    to_phone_number_str(new_individual_data, "phone_no")
    to_phone_number_str(new_individual_data, "phone_no_alternative")
    to_date_string(new_individual_data, "birth_date")
    verify_flex_fields(flex_fields, "individuals")

    individual_data_with_approve_status = {
        to_snake_case(field): {"value": value, "approve_status": False} for field, value in new_individual_data.items()
    }

    for field, field_data in individual_data_with_approve_status.items():
        current_value = getattr(individual, field, None)
        if isinstance(current_value, (datetime, date)):
            current_value = current_value.isoformat()
        elif field in ("phone_no", "phone_no_alternative"):
            current_value = str(current_value)
        individual_data_with_approve_status[field]["previous_value"] = current_value

    documents_with_approve_status = [{"value": document, "approve_status": False} for document in documents]
    documents_to_remove_with_approve_status = [
        {"value": document_id, "approve_status": False} for document_id in documents_to_remove
    ]
    identities_with_approve_status = [{"value": identity, "approve_status": False} for identity in identities]
    identities_to_remove_with_approve_status = [
        {"value": identity_id, "approve_status": False} for identity_id in identities_to_remove
    ]
    flex_fields_with_approve_status = {
        field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
        for field, value in flex_fields.items()
    }
    individual_data_with_approve_status["documents"] = documents_with_approve_status
    individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
    individual_data_with_approve_status["identities"] = identities_with_approve_status
    individual_data_with_approve_status["identities_to_remove"] = identities_to_remove_with_approve_status
    individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status

    individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
        documents_to_remove_with_approve_status
    )
    individual_data_with_approve_status["previous_identities"] = prepare_previous_identities(
        identities_to_remove_with_approve_status
    )

    ticket_details.individual_data = individual_data_with_approve_status
    ticket_details.save()
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    individual_data_update_issue_type_extras = data_change_extras.get("individual_delete_issue_type_extras")

    individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
    individual_id = decode_id_string(individual_encoded_id)
    individual = get_object_or_404(Individual, id=individual_id)
    ticket_individual_data_update_details = TicketDeleteIndividualDetails(
        individual=individual,
        ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    add_individual_issue_type_extras = data_change_extras.get("add_individual_issue_type_extras")

    household_encoded_id = add_individual_issue_type_extras.get("household")
    household_id = decode_id_string(household_encoded_id)
    household = get_object_or_404(Household, id=household_id)
    individual_data = add_individual_issue_type_extras.get("individual_data", {})
    to_phone_number_str(individual_data, "phone_no")
    to_phone_number_str(individual_data, "phone_no_alternative")
    to_date_string(individual_data, "birth_date")
    individual_data = {to_snake_case(key): value for key, value in individual_data.items()}
    flex_fields = {to_snake_case(field): value for field, value in individual_data.pop("flex_fields", {}).items()}
    verify_flex_fields(flex_fields, "individuals")
    individual_data["flex_fields"] = flex_fields
    ticket_add_individual_details = TicketAddIndividualDetails(
        individual_data=individual_data,
        household=household,
        ticket=grievance_ticket,
    )
    ticket_add_individual_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    ticket_details = grievance_ticket.add_individual_ticket_details
    new_add_individual_extras = extras.get("add_individual_issue_type_extras")

    new_individual_data = new_add_individual_extras.get("individual_data", {})
    to_phone_number_str(new_individual_data, "phone_no")
    to_phone_number_str(new_individual_data, "phone_no_alternative")
    to_date_string(new_individual_data, "birth_date")
    new_individual_data = {to_snake_case(key): value for key, value in new_individual_data.items()}
    flex_fields = {to_snake_case(field): value for field, value in new_individual_data.pop("flex_fields", {}).items()}
    verify_flex_fields(flex_fields, "individuals")
    new_individual_data["flex_fields"] = flex_fields

    ticket_details.individual_data = new_individual_data
    ticket_details.approve_status = False
    ticket_details.save()

    grievance_ticket.refresh_from_db()
    return grievance_ticket


def close_add_individual_grievance_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.add_individual_ticket_details
    if not ticket_details or ticket_details.approve_status is False:
        return

    household = ticket_details.household
    individual_data = ticket_details.individual_data
    documents = individual_data.pop("documents", [])
    identities = individual_data.pop("identities", [])
    role = individual_data.pop("role", ROLE_NO_ROLE)
    first_registration_date = timezone.now()
    individual = Individual(
        household=household,
        first_registration_date=first_registration_date,
        last_registration_date=first_registration_date,
        business_area=grievance_ticket.business_area,
        **individual_data,
    )

    documents_to_create = [handle_add_document(document, individual) for document in documents]
    identities_to_create = [handle_add_identity(identity, individual) for identity in identities]

    relationship_to_head_of_household = individual_data.get("relationship")
    if household:
        individual.save()
        if relationship_to_head_of_household == HEAD:
            household.head_of_household = individual
            household.individuals.exclude(id=individual.id).update(relationship=RELATIONSHIP_UNKNOWN)
            household.save(update_fields=["head_of_household"])
        household.size += 1
        household.save()
    else:
        individual.relationship = NON_BENEFICIARY
        individual.save()

    handle_role(role, household, individual)

    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(identities_to_create)

    if individual.household:
        individual.household.recalculate_data()
    else:
        individual.recalculate_data()
    log_create(Individual.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, individual)
    transaction.on_commit(
        lambda: deduplicate_and_check_against_sanctions_list_task.delay(
            should_populate_index=True,
            registration_data_import_id=None,
            individuals_ids=[str(individual.id)],
        )
    )


def close_update_individual_grievance_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.individual_data_update_ticket_details
    if not ticket_details:
        return

    individual = ticket_details.individual
    household = individual.household
    individual_data = ticket_details.individual_data
    role_data = individual_data.pop("role", {})
    flex_fields_with_additional_data = individual_data.pop("flex_fields", {})
    flex_fields = {
        field: data.get("value")
        for field, data in flex_fields_with_additional_data.items()
        if data.get("approve_status") is True
    }
    documents = individual_data.pop("documents", [])
    documents_to_remove_encoded = individual_data.pop("documents_to_remove", [])
    documents_to_remove = [
        decode_id_string(document_data["value"])
        for document_data in documents_to_remove_encoded
        if document_data["approve_status"] is True
    ]
    identities = individual_data.pop("identities", [])
    identities_to_remove_encoded = individual_data.pop("identities_to_remove", [])
    identities_to_remove = [
        identity_data["value"]
        for identity_data in identities_to_remove_encoded
        if identity_data["approve_status"] is True
    ]

    only_approved_data = {
        field: value_and_approve_status.get("value")
        for field, value_and_approve_status in individual_data.items()
        if value_and_approve_status.get("approve_status") is True and field != "previous_documents"
    }
    old_individual = copy_model_object(individual)
    merged_flex_fields = {}
    cast_flex_fields(flex_fields)
    if individual.flex_fields is not None:
        merged_flex_fields.update(individual.flex_fields)
    merged_flex_fields.update(flex_fields)
    Individual.objects.filter(id=individual.id).update(flex_fields=merged_flex_fields, **only_approved_data)
    new_individual = Individual.objects.get(id=individual.id)
    relationship_to_head_of_household = individual_data.get("relationship")
    if (
        household
        and relationship_to_head_of_household
        and relationship_to_head_of_household.get("value") == HEAD
        and relationship_to_head_of_household.get("approve_status")
        and individual.relationship != HEAD
    ):
        if household.individuals.filter(relationship=HEAD).count() > 1:
            raise GraphQLError("There is one head of household. First, you need to change its role.")
        household.head_of_household = individual
        household.save()

    reassign_roles_on_update(individual, ticket_details.role_reassign_data, info)
    if role_data.get("approve_status") is True:
        handle_role(role_data.get("value"), household, individual)

    documents_to_create = [
        handle_add_document(document_data["value"], individual)
        for document_data in documents
        if document_data["approve_status"] is True
    ]
    identities_to_create = [
        handle_add_identity(identity_data["value"], individual)
        for identity_data in identities
        if identity_data["approve_status"] is True
    ]
    Document.objects.bulk_create(documents_to_create)
    Document.objects.filter(id__in=documents_to_remove).delete()
    IndividualIdentity.objects.bulk_create(identities_to_create)
    IndividualIdentity.objects.filter(id__in=identities_to_remove).delete()
    new_individual.refresh_from_db()
    if new_individual.household:
        new_individual.household.recalculate_data()
    else:
        new_individual.recalculate_data()
    log_create(Individual.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, old_individual, new_individual)
    transaction.on_commit(
        lambda: deduplicate_and_check_against_sanctions_list_task.delay(
            should_populate_index=True,
            registration_data_import_id=None,
            individuals_ids=[str(individual.id)],
        )
    )

def cast_flex_fields(flex_fields):
    decimals_flex_attrs_name_list=FlexibleAttribute.objects.filter(type="DECIMAL").values_list("name", flat=True)
    integer_flex_attrs_name_list = FlexibleAttribute.objects.filter(type="INTEGER").values_list("name", flat=True)
    for key, value in flex_fields.items():
        if key in decimals_flex_attrs_name_list:
            flex_fields[key] = float(value)
        if key in integer_flex_attrs_name_list:
            flex_fields[key] = int(value)

def close_update_household_grievance_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.household_data_update_ticket_details
    if not ticket_details:
        return

    household = ticket_details.household
    household_data = ticket_details.household_data
    country_origin = household_data.get("country_origin", {})
    flex_fields_with_additional_data = household_data.pop("flex_fields", {})
    flex_fields = {
        field: data.get("value")
        for field, data in flex_fields_with_additional_data.items()
        if data.get("approve_status") is True
    }
    if country_origin.get("value") is not None:
        household_data["country_origin"]["value"] = Country(country_origin.get("value"))
    country = household_data.get("country", {})
    if country.get("value") is not None:
        household_data["country"]["value"] = Country(country.get("value"))
    only_approved_data = {
        field: value_and_approve_status.get("value")
        for field, value_and_approve_status in household_data.items()
        if value_and_approve_status.get("approve_status") is True
    }
    old_household = copy_model_object(household)
    merged_flex_fields = {}
    cast_flex_fields(flex_fields)
    if household.flex_fields is not None:
        merged_flex_fields.update(household.flex_fields)
    merged_flex_fields.update(flex_fields)
    Household.objects.filter(id=household.id).update(flex_fields=merged_flex_fields, **only_approved_data)
    new_household = Household.objects.get(id=household.id)
    new_household.recalculate_data()
    log_create(Household.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, old_household, new_household)


def close_delete_individual_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.ticket_details
    if not ticket_details or ticket_details.approve_status is False:
        return
    individual_to_remove = ticket_details.individual
    household = None
    if individual_to_remove.household:
        household = individual_to_remove.household
    withdraw_individual_and_reassign_roles(ticket_details, individual_to_remove, info)
    if household:
        household.refresh_from_db()
        household.recalculate_data()
