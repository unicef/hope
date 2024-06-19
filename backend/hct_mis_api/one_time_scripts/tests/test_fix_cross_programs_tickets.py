from django.db.models import F

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, PartnerFactory
from hct_mis_api.apps.grievance.fixtures import TicketNeedsAdjudicationDetailsFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory, create_household
from hct_mis_api.apps.household.models import Document, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.fix_cross_programs_tickets import (
    fix_cross_programs_tickets,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture()
def afghanistan() -> BusinessAreaFactory:
    yield BusinessAreaFactory(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "kobo_token": "XXX",
        },
    )


class TestFixCrossProgramsTickets:
    @pytest.fixture(autouse=True)
    def setup(self, afghanistan: BusinessAreaFactory) -> None:
        self.afghanistan = afghanistan
        PartnerFactory(name="UNICEF")
        (self.program1, self.program2) = ProgramFactory.create_batch(2)

        _, (individual1,) = create_household({"size": 1, "program": self.program1})
        _, (individual2,) = create_household({"size": 1, "program": self.program2})
        _, (individual3,) = create_household({"size": 1, "program": self.program2})

        document_type = DocumentTypeFactory()
        Document.objects.create(
            type=document_type,
            document_number="123123213",
            individual=individual1,
            program=self.program1,
            status=Document.STATUS_VALID,
        )
        Document.objects.create(
            type=document_type,
            document_number="123123213",
            individual=individual2,
            program=self.program2,
            status=Document.STATUS_NEED_INVESTIGATION,
        )
        Document.objects.create(
            type=document_type,
            document_number="123123213",
            individual=individual3,
            program=self.program2,
            status=Document.STATUS_NEED_INVESTIGATION,
        )

        self._create_ticket(individual1, individual2)
        self._create_ticket(individual1, individual3)

    def _create_ticket(self, individual1: Individual, individual2: Individual) -> None:
        ticket = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1,
        )
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        ticket.ticket.programs.add(individual1.program)
        ticket.possible_duplicates.add(individual2)
        ticket.save()

    def test_close_invalid_cross_program_tickets(self) -> None:
        tickets = (
            TicketNeedsAdjudicationDetails.objects.filter(possible_duplicates__program_id__isnull=False)
            .exclude(golden_records_individual__program_id=F("possible_duplicates__program_id"))
            .exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        )
        num_of_tickets = tickets.count()
        assert num_of_tickets == 2

        fix_cross_programs_tickets()

        num_of_tickets = tickets.count()
        assert num_of_tickets == 0

    def test_add_comment_to_cross_program_tickets(self) -> None:
        fix_cross_programs_tickets()
        comment = "Invalid ticket. Closed automatically by the system."
        num_of_tickets = GrievanceTicket.objects.filter(comments=comment).count()

        assert num_of_tickets == 2

    def test_new_tickets_from_the_same_program_should_be_created(self) -> None:
        fix_cross_programs_tickets()

        all_tickets = GrievanceTicket.objects.count()
        new_created_tickets = TicketNeedsAdjudicationDetails.objects.filter(
            golden_records_individual__program_id=F("possible_duplicates__program_id")
        ).count()
        assert all_tickets == 3
        assert new_created_tickets == 1

    def test_should_fix_documents_status(self) -> None:
        fix_cross_programs_tickets()

        assert Document.objects.filter(status=Document.STATUS_VALID).count() == 2
        assert Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count() == 1

    def test_registration_data_import_in_ticket_should_be_the_same_as_in_possible_duplicates(self) -> None:
        fix_cross_programs_tickets()

        ticket = TicketNeedsAdjudicationDetails.objects.get(ticket__status=GrievanceTicket.STATUS_NEW)
        rdi_from_individual = ticket.possible_duplicates.first().registration_data_import_id
        rdi_from_ticket = ticket.ticket.registration_data_import_id
        assert rdi_from_individual == rdi_from_ticket
