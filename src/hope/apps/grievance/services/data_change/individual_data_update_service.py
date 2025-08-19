import dataclasses
from datetime import date, datetime
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.models import log_create
from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.utils import to_snake_case
from hope.apps.geo.models import Area, Country
from hope.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task_single_individual,
)
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
)
from hope.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hope.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    convert_to_empty_string_if_null,
    handle_add_account,
    handle_add_document,
    handle_add_identity,
    handle_document,
    handle_edit_document,
    handle_edit_identity,
    handle_role,
    handle_update_account,
    is_approved,
    prepare_edit_accounts_save,
    prepare_edit_documents,
    prepare_edit_identities,
    prepare_previous_documents,
    prepare_previous_identities,
    save_images,
    to_date_string,
    to_phone_number_str,
    update_es,
    verify_flex_fields,
)
from hope.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_update_service,
)
from hope.apps.household.models import (
    HEAD,
    Document,
    Household,
    Individual,
    IndividualIdentity,
)
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.apps.payment.models import Account
from hope.apps.utils.phone import is_valid_phone_number


@dataclasses.dataclass
class AccountPayloadField:
    name: str
    value: str | None = None
    previous_value: str | None = None


@dataclasses.dataclass
class AccountPayload:
    id: str
    name: str
    approve_status: bool
    data_fields: list[AccountPayloadField]


class IndividualDataUpdateService(DataChangeService):
    def save(self) -> list[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        individual_data_update_issue_type_extras = data_change_extras.get("individual_data_update_issue_type_extras")
        individual = individual_data_update_issue_type_extras.get("individual")
        individual_data = individual_data_update_issue_type_extras.get("individual_data", {})
        documents = individual_data.pop("documents", [])
        documents_to_remove = individual_data.pop("documents_to_remove", [])
        documents_to_edit = individual_data.pop("documents_to_edit", [])
        identities = individual_data.pop("identities", [])
        identities_to_remove = individual_data.pop("identities_to_remove", [])
        identities_to_edit = individual_data.pop("identities_to_edit", [])
        accounts = individual_data.pop("accounts", [])
        accounts_to_edit = individual_data.pop("accounts_to_edit", [])
        to_phone_number_str(individual_data, "phone_no")
        to_phone_number_str(individual_data, "phone_no_alternative")
        to_phone_number_str(individual_data, "payment_delivery_phone_no")
        to_date_string(individual_data, "birth_date")
        flex_fields = {to_snake_case(field): value for field, value in individual_data.pop("flex_fields", {}).items()}
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        individual_data_with_approve_status: dict[str, Any] = {
            to_snake_case(field): {"value": value, "approve_status": False} for field, value in individual_data.items()
        }
        for field in individual_data_with_approve_status:
            current_value = getattr(individual, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            elif field in (
                "phone_no",
                "phone_no_alternative",
                "payment_delivery_phone_no",
            ):
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
        accounts_with_approve_status = [{"value": account, "approve_status": False} for account in accounts]
        flex_fields_with_approve_status = {
            field: {
                "value": value,
                "approve_status": False,
                "previous_value": individual.flex_fields.get(field),
            }
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
        individual_data_with_approve_status["accounts"] = accounts_with_approve_status
        individual_data_with_approve_status["accounts_to_edit"] = prepare_edit_accounts_save(accounts_to_edit)
        individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status

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
        flex_fields = {
            to_snake_case(field): value for field, value in new_individual_data.pop("flex_fields", {}).items()
        }
        to_phone_number_str(new_individual_data, "phone_no")
        to_phone_number_str(new_individual_data, "phone_no_alternative")
        to_phone_number_str(new_individual_data, "payment_delivery_phone_no")
        to_date_string(new_individual_data, "birth_date")
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        individual_data_with_approve_status: dict[str, Any] = {
            to_snake_case(field): {"value": value, "approve_status": False}
            for field, value in new_individual_data.items()
        }
        for field in individual_data_with_approve_status:
            current_value = getattr(individual, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            elif field in (
                "phone_no",
                "phone_no_alternative",
                "payment_delivery_phone_no",
            ):
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
        flex_fields_with_approve_status = {
            field: {
                "value": value,
                "approve_status": False,
                "previous_value": individual.flex_fields.get(field),
            }
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
        individual_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
        ticket_details.individual_data = individual_data_with_approve_status
        ticket_details.save()
        self.grievance_ticket.refresh_from_db()
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.individual_data_update_ticket_details
        program_qs = self.grievance_ticket.programs.all()
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
        documents_to_remove_list = individual_data.pop("documents_to_remove", [])
        documents_to_remove = [
            document_data["value"] for document_data in documents_to_remove_list if is_approved(document_data)
        ]
        documents_to_edit = [
            document for document in individual_data.pop("documents_to_edit", []) if is_approved(document)
        ]
        identities = [identity["value"] for identity in individual_data.pop("identities", []) if is_approved(identity)]
        identities_to_remove_list = individual_data.pop("identities_to_remove", [])
        identities_to_remove = [
            identity_data["value"] for identity_data in identities_to_remove_list if is_approved(identity_data)
        ]
        identities_to_edit = [
            identity for identity in individual_data.pop("identities_to_edit", []) if is_approved(identity)
        ]
        accounts = [account["value"] for account in individual_data.pop("accounts", []) if is_approved(account)]
        accounts_to_edit = [account for account in individual_data.pop("accounts_to_edit", []) if is_approved(account)]
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

        if "phone_no" in only_approved_data:
            only_approved_data["phone_no_valid"] = is_valid_phone_number(only_approved_data["phone_no"])

        if "phone_no_alternative" in only_approved_data:
            only_approved_data["phone_no_alternative_valid"] = is_valid_phone_number(
                only_approved_data["phone_no_alternative"]
            )
        # people update
        hh_fields = [
            "consent",
            "residence_status",
            "country_origin",
            "country",
            "address",
            "village",
            "currency",
            "unhcr_id",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "registration_method",
            "admin_area_title",
        ]
        # move HH fields from only_approved_data into hh_approved_data
        hh_approved_data = {hh_f: only_approved_data.pop(hh_f) for hh_f in hh_fields if hh_f in only_approved_data}
        if hh_approved_data:
            if hh_country_origin := hh_approved_data.get("country_origin"):
                hh_approved_data["country_origin"] = Country.objects.filter(iso_code3=hh_country_origin).first()
            if hh_country := hh_approved_data.get("country"):
                hh_approved_data["country"] = Country.objects.filter(iso_code3=hh_country).first()
            admin_area_title = hh_approved_data.pop("admin_area_title", None)
            # people update HH
            Household.objects.filter(id=household.id).update(**hh_approved_data, updated_at=timezone.now())
            updated_household = Household.objects.get(id=household.id)
            if admin_area_title:
                area = Area.objects.filter(p_code=admin_area_title).first()
                updated_household.set_admin_areas(area)

        # upd Individual
        Individual.objects.filter(id=new_individual.id).update(
            flex_fields=merged_flex_fields,
            **only_approved_data,
            updated_at=timezone.now(),
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
                raise ValidationError("There is one head of household. First, you need to change its role.")
            household = Household.objects.select_for_update().get(id=household.id)
            household.head_of_household = new_individual
            household.save()
        reassign_roles_on_update_service(new_individual, details.role_reassign_data, user, program_qs)
        if is_approved(role_data):
            handle_role(role_data.get("value"), household, new_individual)
        documents_to_create = [handle_add_document(document, new_individual) for document in documents]
        documents_to_update = [handle_edit_document(document.get("value", {})) for document in documents_to_edit]
        identities_to_create = [handle_add_identity(identity, new_individual) for identity in identities]
        identities_to_update = [handle_edit_identity(identity) for identity in identities_to_edit]
        accounts_to_create = [handle_add_account(account, new_individual) for account in accounts]
        accounts_to_update = [handle_update_account(account) for account in accounts_to_edit]

        Account.objects.bulk_update(accounts_to_update, ["data", "number", "financial_institution"])
        Account.objects.bulk_create(accounts_to_create)
        Account.validate_uniqueness(accounts_to_update)  # type: ignore
        Account.validate_uniqueness(accounts_to_create)
        Document.objects.bulk_create(documents_to_create)
        Document.objects.bulk_update(documents_to_update, ["document_number", "type", "photo", "country"])
        Document.objects.filter(id__in=documents_to_remove).delete()
        IndividualIdentity.objects.bulk_create(identities_to_create)
        IndividualIdentity.objects.bulk_update(identities_to_update, ["number", "partner"])
        IndividualIdentity.objects.filter(id__in=identities_to_remove).delete()

        if new_individual.household:
            recalculate_data(new_individual.household)
        else:
            new_individual.recalculate_data()
        new_individual.refresh_from_db()

        log_create(
            Individual.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            program_qs,
            old_individual,
            new_individual,
        )

        update_es(individual)

        if not self.grievance_ticket.business_area.postpone_deduplication:
            transaction.on_commit(
                lambda: deduplicate_and_check_against_sanctions_list_task_single_individual.delay(
                    should_populate_index=True,
                    individuals_ids=[str(new_individual.id)],
                )
            )
