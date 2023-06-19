from datetime import date, datetime
from typing import Any, Dict, List

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from graphql import GraphQLError

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.utils import decode_id_string, to_snake_case
from hct_mis_api.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    convert_to_empty_string_if_null,
    handle_add_document,
    handle_add_identity,
    handle_add_payment_channel,
    handle_document,
    handle_edit_document,
    handle_edit_identity,
    handle_role,
    handle_update_payment_channel,
    is_approved,
    prepare_edit_documents,
    prepare_edit_identities,
    prepare_edit_payment_channel,
    prepare_previous_documents,
    prepare_previous_identities,
    prepare_previous_payment_channels,
    save_images,
    to_date_string,
    to_phone_number_str,
    verify_flex_fields,
)
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_update_service,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
)
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)


class IndividualDataUpdateService(DataChangeService):
    def save(self) -> List[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        individual_data_update_issue_type_extras = data_change_extras.get("individual_data_update_issue_type_extras")
        individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
        individual_id = decode_id_string(individual_encoded_id)
        individual = get_object_or_404(Individual, id=individual_id)
        individual_data = individual_data_update_issue_type_extras.get("individual_data", {})
        documents = individual_data.pop("documents", [])
        documents_to_remove = individual_data.pop("documents_to_remove", [])
        documents_to_edit = individual_data.pop("documents_to_edit", [])
        identities = individual_data.pop("identities", [])
        identities_to_remove = individual_data.pop("identities_to_remove", [])
        identities_to_edit = individual_data.pop("identities_to_edit", [])
        payment_channels = individual_data.pop("payment_channels", [])
        payment_channels_to_remove = individual_data.pop("payment_channels_to_remove", [])
        payment_channels_to_edit = individual_data.pop("payment_channels_to_edit", [])
        to_phone_number_str(individual_data, "phone_no")
        to_phone_number_str(individual_data, "phone_no_alternative")
        to_date_string(individual_data, "birth_date")
        flex_fields = {to_snake_case(field): value for field, value in individual_data.pop("flex_fields", {}).items()}
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        individual_data_with_approve_status: Dict[str, Any] = {
            to_snake_case(field): {"value": value, "approve_status": False} for field, value in individual_data.items()
        }
        for field in individual_data_with_approve_status.keys():
            current_value = getattr(individual, field, None)
            if isinstance(current_value, (datetime, date)):
                current_value = current_value.isoformat()
            elif field in ("phone_no", "phone_no_alternative"):
                current_value = str(current_value)
            elif field == "role":
                current_value = individual.role
            individual_data_with_approve_status[field]["previous_value"] = current_value
        documents_with_approve_status = [
            {"value": handle_document(document), "approve_status": False} for document in documents
        ]
        documents_to_remove_with_approve_status = [
            {"value": document_id, "approve_status": False} for document_id in documents_to_remove
        ]
        identities_with_approve_status = [{"value": identity, "approve_status": False} for identity in identities]
        identities_to_remove_with_approve_status = [
            {"value": identity_id, "approve_status": False} for identity_id in identities_to_remove
        ]
        payment_channels_with_approve_status = [{"value": pc, "approve_status": False} for pc in payment_channels]
        payment_channels_to_remove_with_approve_status = [
            {"value": payment_channel_id, "approve_status": False} for payment_channel_id in payment_channels_to_remove
        ]
        flex_fields_with_approve_status = {
            field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
            for field, value in flex_fields.items()
        }
        individual_data_with_approve_status["documents"] = documents_with_approve_status
        individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
        individual_data_with_approve_status["documents_to_edit"] = prepare_edit_documents(documents_to_edit)
        individual_data_with_approve_status["identities"] = identities_with_approve_status
        individual_data_with_approve_status["identities_to_remove"] = identities_to_remove_with_approve_status
        individual_data_with_approve_status["identities_to_edit"] = prepare_edit_identities(identities_to_edit)
        individual_data_with_approve_status["payment_channels"] = payment_channels_with_approve_status
        individual_data_with_approve_status[
            "payment_channels_to_remove"
        ] = payment_channels_to_remove_with_approve_status
        individual_data_with_approve_status["payment_channels_to_edit"] = prepare_edit_payment_channel(
            payment_channels_to_edit
        )
        individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
        individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
            documents_to_remove_with_approve_status
        )
        individual_data_with_approve_status["previous_identities"] = prepare_previous_identities(
            identities_to_remove_with_approve_status
        )
        individual_data_with_approve_status["previous_payment_channels"] = prepare_previous_payment_channels(
            payment_channels_to_remove_with_approve_status
        )
        ticket_individual_data_update_details = TicketIndividualDataUpdateDetails(
            individual_data=individual_data_with_approve_status,
            individual=individual,
            ticket=self.grievance_ticket,
        )
        ticket_individual_data_update_details.save()
        self.grievance_ticket.refresh_from_db()
        return [self.grievance_ticket]

    def update(self) -> GrievanceTicket:
        ticket_details = self.grievance_ticket.individual_data_update_ticket_details
        individual_data_update_extras = self.extras.get("individual_data_update_issue_type_extras")
        individual = ticket_details.individual
        new_individual_data = individual_data_update_extras.get("individual_data", {})
        documents = new_individual_data.pop("documents", [])
        documents_to_remove = new_individual_data.pop("documents_to_remove", [])
        documents_to_edit = new_individual_data.pop("documents_to_edit", [])
        identities = new_individual_data.pop("identities", [])
        identities_to_remove = new_individual_data.pop("identities_to_remove", [])
        identities_to_edit = new_individual_data.pop("identities_to_edit", [])
        payment_channels = new_individual_data.pop("payment_channels", [])
        payment_channels_to_remove = new_individual_data.pop("payment_channels_to_remove", [])
        payment_channels_to_edit = new_individual_data.pop("payment_channels_to_edit", [])
        flex_fields = {
            to_snake_case(field): value for field, value in new_individual_data.pop("flex_fields", {}).items()
        }
        to_phone_number_str(new_individual_data, "phone_no")
        to_phone_number_str(new_individual_data, "phone_no_alternative")
        to_date_string(new_individual_data, "birth_date")
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        individual_data_with_approve_status: Dict[str, Any] = {
            to_snake_case(field): {"value": value, "approve_status": False}
            for field, value in new_individual_data.items()
        }
        for field in individual_data_with_approve_status.keys():
            current_value = getattr(individual, field, None)
            if isinstance(current_value, (datetime, date)):
                current_value = current_value.isoformat()
            elif field in ("phone_no", "phone_no_alternative"):
                current_value = str(current_value)
            elif field == "role":
                current_value = individual.role
            individual_data_with_approve_status[field]["previous_value"] = current_value
        documents_with_approve_status = [
            {"value": handle_document(document), "approve_status": False} for document in documents
        ]
        documents_to_remove_with_approve_status = [
            {"value": document_id, "approve_status": False} for document_id in documents_to_remove
        ]
        identities_with_approve_status = [{"value": identity, "approve_status": False} for identity in identities]
        identities_to_remove_with_approve_status = [
            {"value": identity_id, "approve_status": False} for identity_id in identities_to_remove
        ]
        payment_channels_with_approve_status = [{"value": pc, "approve_status": False} for pc in payment_channels]
        payment_channels_to_remove_with_approve_status = [
            {"value": payment_channel_id, "approve_status": False} for payment_channel_id in payment_channels_to_remove
        ]
        flex_fields_with_approve_status = {
            field: {"value": value, "approve_status": False, "previous_value": individual.flex_fields.get(field)}
            for field, value in flex_fields.items()
        }
        individual_data_with_approve_status["documents"] = documents_with_approve_status
        individual_data_with_approve_status["documents_to_remove"] = documents_to_remove_with_approve_status
        individual_data_with_approve_status["documents_to_edit"] = prepare_edit_documents(documents_to_edit)
        individual_data_with_approve_status["previous_documents"] = prepare_previous_documents(
            documents_to_remove_with_approve_status
        )
        individual_data_with_approve_status["identities"] = identities_with_approve_status
        individual_data_with_approve_status["identities_to_remove"] = identities_to_remove_with_approve_status
        individual_data_with_approve_status["identities_to_edit"] = prepare_edit_identities(identities_to_edit)
        individual_data_with_approve_status["previous_identities"] = prepare_previous_identities(
            identities_to_remove_with_approve_status
        )
        individual_data_with_approve_status["payment_channels"] = payment_channels_with_approve_status
        individual_data_with_approve_status[
            "payment_channels_to_remove"
        ] = payment_channels_to_remove_with_approve_status
        individual_data_with_approve_status["payment_channels_to_edit"] = prepare_edit_payment_channel(
            payment_channels_to_edit
        )
        individual_data_with_approve_status["previous_payment_channels"] = prepare_previous_payment_channels(
            payment_channels_to_remove_with_approve_status
        )
        individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
        ticket_details.individual_data = individual_data_with_approve_status
        ticket_details.save()
        self.grievance_ticket.refresh_from_db()
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.individual_data_update_ticket_details
        program = self.grievance_ticket.programme
        if not ticket_details:
            return
        details = self.grievance_ticket.individual_data_update_ticket_details
        individual = details.individual
        household = individual.household
        individual_data = details.individual_data
        role_data = individual_data.pop("role", {})
        flex_fields_with_additional_data = individual_data.pop("flex_fields", {})
        flex_fields = {
            field: data.get("value") for field, data in flex_fields_with_additional_data.items() if is_approved(data)
        }
        documents = [document["value"] for document in individual_data.pop("documents", []) if is_approved(document)]
        documents_to_remove_encoded = individual_data.pop("documents_to_remove", [])
        documents_to_remove = [
            decode_id_string(document_data["value"])
            for document_data in documents_to_remove_encoded
            if is_approved(document_data)
        ]
        documents_to_edit = [
            document for document in individual_data.pop("documents_to_edit", []) if is_approved(document)
        ]
        identities = [identity["value"] for identity in individual_data.pop("identities", []) if is_approved(identity)]
        identities_to_remove_encoded = individual_data.pop("identities_to_remove", [])
        identities_to_remove = [
            identity_data["value"] for identity_data in identities_to_remove_encoded if is_approved(identity_data)
        ]
        identities_to_edit = [
            identity for identity in individual_data.pop("identities_to_edit", []) if is_approved(identity)
        ]
        payment_channels = [
            identity["value"] for identity in individual_data.pop("payment_channels", []) if is_approved(identity)
        ]
        payment_channels_to_remove_encoded = individual_data.pop("payment_channels_to_remove", [])
        payment_channels_to_remove = [
            decode_id_string(data["value"]) for data in payment_channels_to_remove_encoded if is_approved(data)
        ]
        payment_channels_to_edit = [
            identity["value"]
            for identity in individual_data.pop("payment_channels_to_edit", [])
            if is_approved(identity)
        ]
        only_approved_data = {
            field: convert_to_empty_string_if_null(value_and_approve_status.get("value"))
            for field, value_and_approve_status in individual_data.items()
            if is_approved(value_and_approve_status) and field != "previous_documents"
        }
        old_individual = copy_model_object(individual)
        merged_flex_fields = {}
        cast_flex_fields(flex_fields)
        if individual.flex_fields is not None:
            merged_flex_fields.update(individual.flex_fields)
        merged_flex_fields.update(flex_fields)
        new_individual = Individual.objects.select_for_update().get(id=individual.id)
        Individual.objects.filter(id=new_individual.id).update(
            flex_fields=merged_flex_fields, **only_approved_data, updated_at=timezone.now()
        )
        relationship_to_head_of_household = individual_data.get("relationship")
        if (
            household
            and relationship_to_head_of_household
            and relationship_to_head_of_household.get("value") == HEAD
            and is_approved(relationship_to_head_of_household)
            and new_individual.relationship != HEAD
        ):
            if household.individuals.filter(relationship=HEAD).count() > 1:
                raise GraphQLError("There is one head of household. First, you need to change its role.")
            household = Household.objects.select_for_update().get(id=household.id)
            household.head_of_household = new_individual
            household.save()
        reassign_roles_on_update_service(new_individual, details.role_reassign_data, user, program)
        if is_approved(role_data):
            handle_role(role_data.get("value"), household, new_individual)
        documents_to_create = [handle_add_document(document, new_individual) for document in documents]
        documents_to_update = [handle_edit_document(document) for document in documents_to_edit]
        identities_to_create = [handle_add_identity(identity, new_individual) for identity in identities]
        identities_to_update = [handle_edit_identity(identity) for identity in identities_to_edit]
        payment_channels_to_create = [
            handle_add_payment_channel(payment_channel, new_individual) for payment_channel in payment_channels
        ]
        payment_channels_to_update = [
            handle_update_payment_channel(payment_channel) for payment_channel in payment_channels_to_edit
        ]
        Document.objects.bulk_create(documents_to_create)
        Document.objects.bulk_update(documents_to_update, ["document_number", "type", "photo"])
        Document.objects.filter(id__in=documents_to_remove).delete()
        IndividualIdentity.objects.bulk_create(identities_to_create)
        IndividualIdentity.objects.bulk_update(identities_to_update, ["number", "partner"])
        IndividualIdentity.objects.filter(id__in=identities_to_remove).delete()
        BankAccountInfo.objects.bulk_create(payment_channels_to_create)
        BankAccountInfo.objects.bulk_update(payment_channels_to_update, ["bank_name", "bank_account_number"])
        BankAccountInfo.objects.filter(id__in=payment_channels_to_remove).delete()
        if new_individual.household:
            recalculate_data(new_individual.household)
        else:
            new_individual.recalculate_data()
        new_individual.refresh_from_db()

        log_create(Individual.ACTIVITY_LOG_MAPPING, "business_area", user, program, old_individual, new_individual)
        if not self.grievance_ticket.business_area.postpone_deduplication:
            transaction.on_commit(
                lambda: deduplicate_and_check_against_sanctions_list_task.delay(
                    should_populate_index=True,
                    individuals_ids=[str(new_individual.id)],
                )
            )
