from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.utils import decode_id_string, to_snake_case
from hct_mis_api.apps.grievance.celery_tasks import (
    deduplicate_and_check_against_sanctions_list_task,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.grievance.services.data_change.utils import (
    handle_add_document,
    handle_add_identity,
    handle_add_payment_channel,
    handle_documents,
    handle_role,
    save_images,
    to_date_string,
    to_phone_number_str,
    verify_flex_fields,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    RELATIONSHIP_UNKNOWN,
    ROLE_NO_ROLE,
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualCollection,
    IndividualIdentity,
)
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.utils.querysets import evaluate_qs


class AddIndividualService(DataChangeService):
    def save(self) -> List[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        add_individual_issue_type_extras = data_change_extras.get("add_individual_issue_type_extras")
        household_encoded_id = add_individual_issue_type_extras.get("household")
        household_id = decode_id_string(household_encoded_id)
        household = get_object_or_404(Household, id=household_id)
        individual_data = add_individual_issue_type_extras.get("individual_data", {})
        documents = individual_data.pop("documents", [])
        to_phone_number_str(individual_data, "phone_no")
        to_phone_number_str(individual_data, "phone_no_alternative")
        to_date_string(individual_data, "birth_date")
        individual_data = {to_snake_case(key): value for key, value in individual_data.items()}
        flex_fields = {to_snake_case(field): value for field, value in individual_data.pop("flex_fields", {}).items()}
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        individual_data["flex_fields"] = flex_fields
        individual_data["documents"] = handle_documents(documents)
        ticket_add_individual_details = TicketAddIndividualDetails(
            individual_data=individual_data,
            household=household,
            ticket=self.grievance_ticket,
        )
        ticket_add_individual_details.save()
        self.grievance_ticket.refresh_from_db()
        return [self.grievance_ticket]

    def update(self) -> GrievanceTicket:
        ticket_details = self.grievance_ticket.add_individual_ticket_details
        new_add_individual_extras = self.extras.get("add_individual_issue_type_extras")
        new_individual_data = new_add_individual_extras.get("individual_data", {})
        documents = new_individual_data.pop("documents", [])
        to_phone_number_str(new_individual_data, "phone_no")
        to_phone_number_str(new_individual_data, "phone_no_alternative")
        to_date_string(new_individual_data, "birth_date")
        new_individual_data = {to_snake_case(key): value for key, value in new_individual_data.items()}
        flex_fields = {
            to_snake_case(field): value for field, value in new_individual_data.pop("flex_fields", {}).items()
        }
        verify_flex_fields(flex_fields, "individuals")
        save_images(flex_fields, "individuals")
        new_individual_data["flex_fields"] = flex_fields
        new_individual_data["documents"] = handle_documents(documents)
        ticket_details.individual_data = new_individual_data
        ticket_details.approve_status = False
        ticket_details.save()
        self.grievance_ticket.refresh_from_db()
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.add_individual_ticket_details
        if not ticket_details or ticket_details.approve_status is False:
            return
        details = self.grievance_ticket.add_individual_ticket_details
        household = Household.objects.select_for_update().get(id=details.household.id)
        individual_data = details.individual_data
        documents = individual_data.pop("documents", [])
        identities = individual_data.pop("identities", [])
        payment_channels = individual_data.pop("payment_channels", [])
        role = individual_data.pop("role", ROLE_NO_ROLE)
        first_registration_date = timezone.now()
        individual = Individual.objects.create(
            household=household,
            first_registration_date=first_registration_date,
            last_registration_date=first_registration_date,
            business_area=self.grievance_ticket.business_area,
            individual_collection=IndividualCollection.objects.create(),
            **individual_data,
        )
        individual.refresh_from_db()
        documents_to_create = [handle_add_document(document, individual) for document in documents]
        identities_to_create = [handle_add_identity(identity, individual) for identity in identities]
        payment_channels_to_create = [handle_add_payment_channel(pc, individual) for pc in payment_channels]
        relationship_to_head_of_household = individual_data.get("relationship")
        if household:
            individual.save()
            if relationship_to_head_of_household == HEAD:
                household.head_of_household = individual
                household_individuals = evaluate_qs(household.individuals.exclude(id=individual.id).select_for_update())
                household_individuals.update(relationship=RELATIONSHIP_UNKNOWN)
                household.save(update_fields=["head_of_household"])
            household.size += 1
            household.save()
        else:
            individual.relationship = NON_BENEFICIARY
            individual.save()
        handle_role(role, household, individual)
        Document.objects.bulk_create(documents_to_create)
        IndividualIdentity.objects.bulk_create(identities_to_create)
        BankAccountInfo.objects.bulk_create(payment_channels_to_create)
        if household:
            recalculate_data(household)
        else:
            individual.recalculate_data()
        log_create(
            Individual.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            self.grievance_ticket.programs.all(),
            None,
            individual,
        )
        if not self.grievance_ticket.business_area.postpone_deduplication:
            transaction.on_commit(
                lambda: deduplicate_and_check_against_sanctions_list_task.delay(
                    should_populate_index=True,
                    individuals_ids=[str(individual.id)],
                )
            )
