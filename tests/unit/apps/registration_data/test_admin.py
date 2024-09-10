from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    Document,
    Household,
    Individual,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.admin import RegistrationDataImportAdmin
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.apps.utils.models import MergeStatusModel


class RegistrationDataImportAdminDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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

    def test_delete_rdi(self) -> None:
        self.assertEqual(RegistrationDataImport.objects.count(), 1)

        self.assertEqual(PendingHousehold.objects.count(), 1)
        self.assertEqual(PendingIndividual.objects.count(), 2)
        self.assertEqual(PendingDocument.objects.count(), 1)

        RegistrationDataImportAdmin._delete_rdi(self.rdi)

        self.assertEqual(RegistrationDataImport.objects.count(), 0)
        with self.assertRaises(RegistrationDataImport.DoesNotExist):
            RegistrationDataImport.objects.get(id=self.rdi.id)

        self.assertEqual(PendingHousehold.objects.count(), 0)
        self.assertEqual(PendingIndividual.objects.count(), 0)
        self.assertEqual(PendingDocument.objects.count(), 0)


class RegistrationDataImportAdminDeleteMergedTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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

        cls.target_population = TargetPopulationFactory(business_area=afghanistan, program=program)
        cls.household_selection = HouseholdSelectionFactory(
            household=cls.household, target_population=cls.target_population
        )

    def test_delete_merged_rdi(self) -> None:
        self.assertEqual(GrievanceTicket.objects.count(), 2)
        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 1)
        self.assertEqual(TicketComplaintDetails.objects.count(), 1)
        self.assertEqual(HouseholdSelection.objects.count(), 1)

        self.assertEqual(RegistrationDataImport.objects.count(), 1)

        self.assertEqual(Household.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 2)
        self.assertEqual(Document.objects.count(), 1)

        RegistrationDataImportAdmin._delete_merged_rdi(self.rdi)

        self.assertEqual(GrievanceTicket.objects.count(), 0)
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket1.id).first())
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket2.id).first())

        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 0)
        self.assertIsNone(TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket2).first())

        self.assertEqual(TicketComplaintDetails.objects.count(), 0)
        self.assertIsNone(TicketComplaintDetails.objects.filter(ticket=self.grievance_ticket1).first())

        self.assertEqual(HouseholdSelection.objects.count(), 0)
        self.assertIsNone(HouseholdSelection.objects.filter(household=self.household).first())

        self.assertEqual(RegistrationDataImport.objects.count(), 0)
        self.assertIsNone(RegistrationDataImport.objects.filter(id=self.rdi.id).first())

        self.assertEqual(Household.objects.count(), 0)
        self.assertIsNone(Household.objects.filter(id=self.household.id).first())

        self.assertEqual(Individual.objects.count(), 0)
        self.assertIsNone(Individual.objects.filter(id=self.individuals[0].id).first())

        self.assertEqual(Document.objects.count(), 0)
        self.assertIsNone(Document.objects.filter(id=self.document.id).first())
