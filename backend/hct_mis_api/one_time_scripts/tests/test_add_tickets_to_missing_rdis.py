from typing import Optional, Tuple

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.grievance.fixtures import (
    TicketAddIndividualDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory
from hct_mis_api.one_time_scripts.add_tickets_to_missing_rdis import (
    create_tickets_for_missing_rdis,
)


class TestAddTicketsToMissingRDIS(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.program = ProgramFactory(name="program1", business_area=self.business_area, status=Program.ACTIVE)
        self.other_program = ProgramFactory(name="program2", business_area=self.business_area, status=Program.ACTIVE)
        self.rdi = RegistrationDataImportFactory(business_area=self.business_area, program=self.program)
        (
            self.original_household,
            self.original_individual,
            self.household_representation,
            self.individual_representation,
        ) = self.create_household_with_representations(self.program)
        self.original_household.registration_data_import = self.rdi
        self.original_household.save()
        self.household_representation.registration_data_import = self.rdi
        self.household_representation.save()

        self.add_individual_details = TicketAddIndividualDetailsFactory(
            household=self.original_household,
        )
        ticket = self.add_individual_details.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket.save()

        self.delete_household_details1 = TicketDeleteHouseholdDetailsFactory(
            household=self.original_household,
        )
        ticket = self.delete_household_details1.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket.save()

        self.delete_household_details2 = TicketDeleteHouseholdDetailsFactory(
            household=self.original_household,
        )
        ticket = self.delete_household_details2.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket.save()

        self.delete_household_details3 = TicketDeleteHouseholdDetailsFactory(
            household=self.original_household,
        )
        delete_household_details3_repr = TicketDeleteHouseholdDetailsFactory(
            household=self.original_household,
        )
        ticket_repr = delete_household_details3_repr.ticket
        ticket_repr.programs.set([self.other_program])
        ticket_repr.copied_from = self.delete_household_details3.ticket
        ticket_repr.save()

        ticket = self.delete_household_details3.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket.save()

        self.individual_data_update_details = TicketIndividualDataUpdateDetailsFactory(
            individual=self.original_individual
        )
        ticket = self.individual_data_update_details.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket.save()

        self.system_flagging_details = TicketSystemFlaggingDetailsFactory(
            sanction_list_individual=SanctionListIndividualFactory(),
            golden_records_individual=self.original_individual,
        )
        ticket = self.system_flagging_details.ticket
        ticket.is_original = True
        ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket.save()

        self.golden_rec_needs_adjudication = self.create_individual_with_representations([self.program])

        self.needs_adjudication = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication,
        )
        self.needs_adjudication.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.needs_adjudication.ticket.is_original = True
        self.needs_adjudication.ticket.save()
        self.needs_adjudication.possible_duplicates.set(
            [
                self.original_individual,
            ]
        )
        self.needs_adjudication.selected_individuals.set(
            [
                self.original_individual,
            ]
        )

        # Needs adjudication ticket with existing representation in program
        self.golden_rec_needs_adjudication_existing = self.create_individual_with_representations([self.program])
        some_other_ind = self.create_individual_with_representations([self.program])
        some_other_ind_repr = some_other_ind.copied_to.filter(program=self.program).first()

        self.needs_adjudication_existing_org = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication_existing,
        )
        self.needs_adjudication_existing_org.possible_duplicates.set(
            [
                self.original_individual,
            ]
        )
        self.needs_adjudication_existing_org.selected_individuals.set(
            [
                self.original_individual,
            ]
        )
        ticket = self.needs_adjudication_existing_org.ticket
        ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket.is_original = True
        ticket.save()

        self.needs_adjudication_existing_repr = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication_existing.copied_to.filter(
                program=self.program
            ).first(),
        )
        ticket_repr = self.needs_adjudication_existing_repr.ticket
        ticket_repr.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket_repr.is_original = False
        ticket_repr.copied_from = ticket
        ticket_repr.programs.set([self.program])
        ticket_repr.save()

        self.needs_adjudication_existing_repr.possible_duplicates.set(
            [
                some_other_ind_repr,
            ]
        )
        self.needs_adjudication_existing_repr.selected_individuals.set(
            [
                some_other_ind_repr,
            ]
        )

    def create_individual_with_representations(
        self,
        representations_programs: Optional[list[Program]] = None,
    ) -> Individual:
        if not representations_programs:
            representations_programs = []
        original_individual = IndividualFactory(
            business_area=self.business_area,
            household=None,
            is_original=True,
        )

        for program in representations_programs:
            IndividualFactory(
                household=None,
                business_area=self.business_area,
                copied_from=original_individual,
                origin_unicef_id=original_individual.unicef_id,
                program=program,
                is_original=False,
            )
        return original_individual

    def create_household_with_representations(
        self,
        program: Program,
    ) -> Tuple[Household, Individual, Household, Individual]:
        original_individual = IndividualFactory(household=None, business_area=self.business_area, is_original=True)
        original_household = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=original_individual,
            is_original=True,
        )
        original_individual.household = original_household
        original_individual.save()

        individual_representation = IndividualFactory(
            household=None,
            business_area=self.business_area,
            program=program,
            copied_from=original_individual,
            is_original=False,
        )
        household_representation = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual_representation,
            copied_from=original_household,
            origin_unicef_id=original_household.unicef_id,
            program=program,
            is_original=False,
        )
        individual_representation.household = household_representation
        individual_representation.save()

        return original_household, original_individual, household_representation, individual_representation

    def create_extra_data_for_needs_adjudication(self, golden_records_ids: list, possible_duplicates_ids: list) -> dict:
        data = {"golden_records": [], "possible_duplicate": []}

        for golden_record_id in golden_records_ids:
            data["golden_records"].append(
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(golden_record_id),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": "score",
                }
            )
        for possible_duplicate_id in possible_duplicates_ids:
            data["possible_duplicate"].append(
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(possible_duplicate_id),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": "score",
                },
            )
        return data

    def test_add_tickets_to_missing_rdis(self) -> None:
        create_tickets_for_missing_rdis([self.rdi])  # type: ignore
        add_individual_details_repr = (
            self.add_individual_details.ticket.copied_to.filter(programs=self.program)
            .first()
            .add_individual_ticket_details
        )
        self.assertIsNotNone(add_individual_details_repr)
        self.assertEqual(add_individual_details_repr.household, self.household_representation)

        delete_household_details1_repr = (
            self.delete_household_details1.ticket.copied_to.filter(programs=self.program)
            .first()
            .delete_household_ticket_details
        )
        self.assertIsNotNone(delete_household_details1_repr)
        self.assertEqual(delete_household_details1_repr.household, self.household_representation)

        delete_household_details2_repr = (
            self.delete_household_details2.ticket.copied_to.filter(programs=self.program)
            .first()
            .delete_household_ticket_details
        )
        self.assertIsNotNone(delete_household_details2_repr)
        self.assertEqual(delete_household_details2_repr.household, self.household_representation)

        individual_data_update_details_repr = (
            self.individual_data_update_details.ticket.copied_to.filter(programs=self.program)
            .first()
            .individual_data_update_ticket_details
        )
        self.assertIsNotNone(individual_data_update_details_repr)
        self.assertEqual(individual_data_update_details_repr.individual, self.individual_representation)

        system_flagging_details_repr = (
            self.system_flagging_details.ticket.copied_to.filter(programs=self.program)
            .first()
            .system_flagging_ticket_details
        )
        self.assertIsNotNone(system_flagging_details_repr)
        self.assertEqual(system_flagging_details_repr.golden_records_individual, self.individual_representation)

        needs_adjudication_repr = (
            self.needs_adjudication.ticket.copied_to.filter(programs=self.program)
            .first()
            .needs_adjudication_ticket_details
        )
        self.assertIsNotNone(needs_adjudication_repr)
        possible_duplicates = [
            *needs_adjudication_repr.possible_duplicates.all(),
            needs_adjudication_repr.golden_records_individual,
        ]
        expected_possible_duplicates = [
            self.original_individual.copied_to.filter(program=self.program).first(),
            self.golden_rec_needs_adjudication.copied_to.filter(program=self.program).first(),
        ]
        for possible_duplicate in possible_duplicates:
            self.assertIn(possible_duplicate, expected_possible_duplicates)
        self.assertEqual(needs_adjudication_repr.selected_individuals.count(), 1)
        self.assertEqual(needs_adjudication_repr.selected_individuals.first(), self.individual_representation)

        delete_household_details3_repr = self.delete_household_details3.ticket.copied_to.filter(
            programs=self.program
        ).first()
        self.assertIsNone(delete_household_details3_repr)

        self.needs_adjudication_existing_repr.refresh_from_db()
        self.assertEqual(self.needs_adjudication_existing_repr.possible_duplicates.count(), 2)
        self.assertEqual(self.needs_adjudication_existing_repr.selected_individuals.count(), 2)
