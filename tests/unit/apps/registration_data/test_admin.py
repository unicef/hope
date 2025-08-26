import pytest
from django.test import TestCase
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.admin.registration_data import RegistrationDataImportAdmin
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)
from hope.models.household import (
    Household,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hope.models.individual import Individual
from hope.models.document import Document
from hope.models import Payment
from hope.models.registration_data_import import RegistrationDataImport
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class RegistrationDataImportAdminDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        afghanistan = create_afghanistan()
        program = ProgramFactory(name="Test program For RDI", business_area=afghanistan)
        cls.rdi = RegistrationDataImportFactory(
            name="RDI To Remove",
            business_area=afghanistan,
            program=program,
            status=RegistrationDataImport.IN_REVIEW,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": afghanistan,
                "program": program,
                "registration_data_import": cls.rdi,
                "rdi_merge_status": MergeStatusModel.PENDING,
            },
            individuals_data=[
                {
                    "business_area": afghanistan,
                    "program": program,
                    "registration_data_import": cls.rdi,
                    "rdi_merge_status": MergeStatusModel.PENDING,
                },
                {
                    "business_area": afghanistan,
                    "program": program,
                    "registration_data_import": cls.rdi,
                    "rdi_merge_status": MergeStatusModel.PENDING,
                },
            ],
        )

        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=program,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        rebuild_search_index()

    def test_delete_rdi(self) -> None:
        assert RegistrationDataImport.objects.count() == 1

        assert PendingHousehold.objects.count() == 1
        assert PendingIndividual.objects.count() == 2
        assert PendingDocument.objects.count() == 1

        RegistrationDataImportAdmin._delete_rdi(self.rdi)

        assert RegistrationDataImport.objects.count() == 0
        with self.assertRaises(RegistrationDataImport.DoesNotExist):
            RegistrationDataImport.objects.get(id=self.rdi.id)

        assert PendingHousehold.objects.count() == 0
        assert PendingIndividual.objects.count() == 0
        assert PendingDocument.objects.count() == 0


@pytest.mark.elasticsearch
class RegistrationDataImportAdminDeleteMergedTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        afghanistan = create_afghanistan()
        program = ProgramFactory(name="Test program For RDI", business_area=afghanistan)
        cls.rdi = RegistrationDataImportFactory(
            name="RDI To Remove",
            business_area=afghanistan,
            program=program,
            status=RegistrationDataImport.MERGED,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": afghanistan,
                "program": program,
                "registration_data_import": cls.rdi,
                "rdi_merge_status": MergeStatusModel.MERGED,
            },
            individuals_data=[
                {
                    "business_area": afghanistan,
                    "program": program,
                    "registration_data_import": cls.rdi,
                    "rdi_merge_status": MergeStatusModel.MERGED,
                },
                {
                    "business_area": afghanistan,
                    "program": program,
                    "registration_data_import": cls.rdi,
                    "rdi_merge_status": MergeStatusModel.MERGED,
                },
            ],
        )

        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=program,
        )
        cls.grievance_ticket1 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_complaint_details = TicketComplaintDetails.objects.create(
            ticket=cls.grievance_ticket1,
            household=cls.household,
        )
        cls.grievance_ticket2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_CLOSED)
        cls.ticket_individual_data_update = TicketIndividualDataUpdateDetails.objects.create(
            ticket=cls.grievance_ticket2,
            individual=cls.individuals[0],
        )

        cls.payment_plan = PaymentPlanFactory(business_area=afghanistan, program_cycle=program.cycles.first())
        cls.payment = PaymentFactory(household=cls.household, parent=cls.payment_plan)
        rebuild_search_index()

    def test_delete_merged_rdi(self) -> None:
        assert GrievanceTicket.objects.count() == 2
        assert TicketIndividualDataUpdateDetails.objects.count() == 1
        assert TicketComplaintDetails.objects.count() == 1
        assert Payment.objects.count() == 1

        assert RegistrationDataImport.objects.count() == 1

        assert Household.objects.count() == 1
        assert Individual.objects.count() == 2
        assert Document.objects.count() == 1

        RegistrationDataImportAdmin._delete_merged_rdi(self.rdi)

        assert GrievanceTicket.objects.count() == 0
        assert GrievanceTicket.objects.filter(id=self.grievance_ticket1.id).first() is None
        assert GrievanceTicket.objects.filter(id=self.grievance_ticket2.id).first() is None

        assert TicketIndividualDataUpdateDetails.objects.count() == 0
        assert TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket2).first() is None

        assert TicketComplaintDetails.objects.count() == 0
        assert TicketComplaintDetails.objects.filter(ticket=self.grievance_ticket1).first() is None

        assert Payment.objects.count() == 0
        assert Payment.objects.filter(household=self.household).first() is None

        assert RegistrationDataImport.objects.count() == 0
        assert RegistrationDataImport.objects.filter(id=self.rdi.id).first() is None

        assert Household.objects.count() == 0
        assert Household.objects.filter(id=self.household.id).first() is None

        assert Individual.objects.count() == 0
        assert Individual.objects.filter(id=self.individuals[0].id).first() is None

        assert Document.objects.count() == 0
        assert Document.objects.filter(id=self.document.id).first() is None
