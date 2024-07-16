from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
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
from hct_mis_api.apps.household.models import Document, Household, Individual
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentRecord
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.one_time_scripts.delete_pplans_and_rdi import (
    delete_plans_and_rdi_for_nigeria,
    delete_rdi_for_palestine,
)


class TestDeletePPlansAndRDIForNigeria(TestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        nigeria = BusinessAreaFactory(name="Nigeria", slug="nigeria")
        program = ProgramFactory(name="VCM Network for Outbreak response", business_area=nigeria)
        cls.rdi_datahub = RegistrationDataImportDatahubFactory()
        cls.rdi = RegistrationDataImportFactory(
            name="VCM RDI all data Katsina",
            business_area=nigeria,
            program=program,
            datahub_id=cls.rdi_datahub.id,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": nigeria,
                "program": program,
                "registration_data_import": cls.rdi,
            },
            individuals_data=[
                {
                    "business_area": nigeria,
                    "program": program,
                    "registration_data_import": cls.rdi,
                },
                {
                    "business_area": nigeria,
                    "program": program,
                    "registration_data_import": cls.rdi,
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

        cls.target_population = TargetPopulationFactory(business_area=nigeria, program=program)
        cls.household_selection = HouseholdSelectionFactory(
            household=cls.household, target_population=cls.target_population
        )

        cls.payment_record = PaymentRecordFactory(household=cls.household)

        cls.payment_plan1 = PaymentPlanFactory(program=program)
        cls.payment_plan1.unicef_id = "PP-3210-24-00000021"
        cls.payment_plan1.save()
        cls.payment_plan2 = PaymentPlanFactory(program=program)
        cls.payment_plan2.unicef_id = "PP-3210-24-00000022"
        cls.payment_plan2.save()
        cls.payment_plan3 = PaymentPlanFactory(program=program)  # different unicef_id
        cls.payment_plan3.unicef_id = "PP-1111-24-00000000"
        cls.payment_plan3.save()

        program_other = ProgramFactory(name="Other Program", business_area=nigeria)
        cls.rdi_datahub_other = RegistrationDataImportDatahubFactory()
        cls.rdi_other = RegistrationDataImportFactory(
            name="Other RDI",
            business_area=nigeria,
            program=program_other,
            datahub_id=cls.rdi_datahub_other.id,
        )
        cls.household_other, cls.individuals_other = create_household_and_individuals(
            household_data={
                "business_area": nigeria,
                "program": program_other,
                "registration_data_import": cls.rdi_other,
            },
            individuals_data=[
                {
                    "business_area": nigeria,
                    "program": program_other,
                    "registration_data_import": cls.rdi_other,
                },
                {
                    "business_area": nigeria,
                    "program": program_other,
                    "registration_data_import": cls.rdi_other,
                },
            ],
        )
        cls.grievance_ticket_other = GrievanceTicketFactory(status=GrievanceTicket.STATUS_CLOSED)
        cls.ticket_complaint_details_other = TicketIndividualDataUpdateDetails.objects.create(
            ticket=cls.grievance_ticket_other,
            individual=cls.individuals_other[0],
        )
        cls.target_population_other = TargetPopulationFactory(business_area=nigeria, program=program_other)
        cls.household_selection = HouseholdSelectionFactory(
            household=cls.household_other, target_population=cls.target_population_other
        )

        cls.payment_record_other = PaymentRecordFactory(household=cls.household_other)

    def test_delete_plans_and_rdi_for_nigeria(self) -> None:
        self.assertEqual(PaymentPlan.objects.count(), 3)
        self.assertEqual(PaymentRecord.objects.count(), 2)
        self.assertEqual(GrievanceTicket.objects.count(), 3)
        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 2)
        self.assertEqual(TicketComplaintDetails.objects.count(), 1)
        self.assertEqual(HouseholdSelection.objects.count(), 2)
        self.assertEqual(HouseholdSelection.objects.count(), 2)

        self.assertEqual(RegistrationDataImport.objects.count(), 2)
        self.assertEqual(RegistrationDataImportDatahub.objects.count(), 2)

        self.assertEqual(Household.objects.count(), 2)
        self.assertEqual(Individual.objects.count(), 4)
        self.assertEqual(Document.objects.count(), 1)

        delete_plans_and_rdi_for_nigeria()

        self.assertEqual(PaymentPlan.objects.count(), 1)
        self.assertIsNone(PaymentPlan.objects.filter(unicef_id="PP-3210-24-00000021").first())
        self.assertIsNone(PaymentPlan.objects.filter(unicef_id="PP-3210-24-00000022").first())
        self.assertIsNotNone(PaymentPlan.objects.filter(unicef_id="PP-1111-24-00000000").first())

        self.assertEqual(PaymentRecord.objects.count(), 1)
        self.assertIsNone(PaymentRecord.objects.filter(household=self.household).first())
        self.assertIsNotNone(PaymentRecord.objects.filter(household=self.household_other).first())

        self.assertEqual(GrievanceTicket.objects.count(), 1)
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket1.id).first())
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket2.id).first())
        self.assertIsNotNone(GrievanceTicket.objects.filter(id=self.grievance_ticket_other.id).first())

        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 1)
        self.assertIsNone(TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket2).first())
        self.assertIsNotNone(
            TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket_other).first()
        )

        self.assertEqual(TicketComplaintDetails.objects.count(), 0)
        self.assertIsNone(TicketComplaintDetails.objects.filter(ticket=self.grievance_ticket1).first())

        self.assertEqual(HouseholdSelection.objects.count(), 1)
        self.assertIsNone(HouseholdSelection.objects.filter(household=self.household).first())
        self.assertIsNotNone(HouseholdSelection.objects.filter(household=self.household_other).first())

        self.assertEqual(RegistrationDataImport.objects.count(), 1)
        self.assertIsNone(RegistrationDataImport.objects.filter(id=self.rdi.id).first())
        self.assertIsNotNone(RegistrationDataImport.objects.filter(id=self.rdi_other.id).first())

        self.assertEqual(RegistrationDataImportDatahub.objects.count(), 1)
        self.assertIsNone(RegistrationDataImportDatahub.objects.filter(id=self.rdi_datahub.id).first())
        self.assertIsNotNone(RegistrationDataImportDatahub.objects.filter(id=self.rdi_datahub_other.id).first())

        self.assertEqual(Household.objects.count(), 1)
        self.assertIsNone(Household.objects.filter(id=self.household.id).first())
        self.assertIsNotNone(Household.objects.filter(id=self.household_other.id).first())

        self.assertEqual(Individual.objects.count(), 2)
        self.assertIsNone(Individual.objects.filter(id=self.individuals[0].id).first())
        self.assertIsNotNone(Individual.objects.filter(id=self.individuals_other[0].id).first())

        self.assertEqual(Document.objects.count(), 0)
        self.assertIsNone(Document.objects.filter(id=self.document.id).first())


class TestDeletePPlansAndRDIForPalestine(TestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        palestine = BusinessAreaFactory(name="Palestine, State Of", slug="palestine-state-of")
        program = ProgramFactory(name="HCT_Gaza_Response_MPCA_Oct7", business_area=palestine)
        cls.rdi_datahub = RegistrationDataImportDatahubFactory()
        cls.rdi = RegistrationDataImportFactory(
            name="HCT_Gaza_July24_B23.1_1",
            business_area=palestine,
            program=program,
            datahub_id=cls.rdi_datahub.id,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": palestine,
                "program": program,
                "registration_data_import": cls.rdi,
            },
            individuals_data=[
                {
                    "business_area": palestine,
                    "program": program,
                    "registration_data_import": cls.rdi,
                },
                {
                    "business_area": palestine,
                    "program": program,
                    "registration_data_import": cls.rdi,
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

        cls.target_population = TargetPopulationFactory(business_area=palestine, program=program)
        cls.household_selection = HouseholdSelectionFactory(
            household=cls.household, target_population=cls.target_population
        )

        cls.payment_record = PaymentRecordFactory(household=cls.household)

        program_other = ProgramFactory(name="Other Program", business_area=palestine)
        cls.rdi_datahub_other = RegistrationDataImportDatahubFactory()
        cls.rdi_other = RegistrationDataImportFactory(
            name="Other RDI",
            business_area=palestine,
            program=program_other,
            datahub_id=cls.rdi_datahub_other.id,
        )
        cls.household_other, cls.individuals_other = create_household_and_individuals(
            household_data={
                "business_area": palestine,
                "program": program_other,
                "registration_data_import": cls.rdi_other,
            },
            individuals_data=[
                {
                    "business_area": palestine,
                    "program": program_other,
                    "registration_data_import": cls.rdi_other,
                },
                {
                    "business_area": palestine,
                    "program": program_other,
                    "registration_data_import": cls.rdi_other,
                },
            ],
        )
        cls.grievance_ticket_other = GrievanceTicketFactory(status=GrievanceTicket.STATUS_CLOSED)
        cls.ticket_complaint_details_other = TicketIndividualDataUpdateDetails.objects.create(
            ticket=cls.grievance_ticket_other,
            individual=cls.individuals_other[0],
        )
        cls.target_population_other = TargetPopulationFactory(business_area=palestine, program=program_other)
        cls.household_selection = HouseholdSelectionFactory(
            household=cls.household_other, target_population=cls.target_population_other
        )

        cls.payment_record_other = PaymentRecordFactory(household=cls.household_other)

    def test_delete_plans_and_rdi_for_palestine(self) -> None:
        self.assertEqual(PaymentRecord.objects.count(), 2)
        self.assertEqual(GrievanceTicket.objects.count(), 3)
        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 2)
        self.assertEqual(TicketComplaintDetails.objects.count(), 1)
        self.assertEqual(HouseholdSelection.objects.count(), 2)
        self.assertEqual(HouseholdSelection.objects.count(), 2)

        self.assertEqual(RegistrationDataImport.objects.count(), 2)
        self.assertEqual(RegistrationDataImportDatahub.objects.count(), 2)

        self.assertEqual(Household.objects.count(), 2)
        self.assertEqual(Individual.objects.count(), 4)
        self.assertEqual(Document.objects.count(), 1)

        delete_rdi_for_palestine()

        self.assertEqual(PaymentRecord.objects.count(), 1)
        self.assertIsNone(PaymentRecord.objects.filter(household=self.household).first())
        self.assertIsNotNone(PaymentRecord.objects.filter(household=self.household_other).first())

        self.assertEqual(GrievanceTicket.objects.count(), 1)
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket1.id).first())
        self.assertIsNone(GrievanceTicket.objects.filter(id=self.grievance_ticket2.id).first())
        self.assertIsNotNone(GrievanceTicket.objects.filter(id=self.grievance_ticket_other.id).first())

        self.assertEqual(TicketIndividualDataUpdateDetails.objects.count(), 1)
        self.assertIsNone(TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket2).first())
        self.assertIsNotNone(
            TicketIndividualDataUpdateDetails.objects.filter(ticket=self.grievance_ticket_other).first()
        )

        self.assertEqual(TicketComplaintDetails.objects.count(), 0)
        self.assertIsNone(TicketComplaintDetails.objects.filter(ticket=self.grievance_ticket1).first())

        self.assertEqual(HouseholdSelection.objects.count(), 1)
        self.assertIsNone(HouseholdSelection.objects.filter(household=self.household).first())
        self.assertIsNotNone(HouseholdSelection.objects.filter(household=self.household_other).first())

        self.assertEqual(RegistrationDataImport.objects.count(), 1)
        self.assertIsNone(RegistrationDataImport.objects.filter(id=self.rdi.id).first())
        self.assertIsNotNone(RegistrationDataImport.objects.filter(id=self.rdi_other.id).first())

        self.assertEqual(RegistrationDataImportDatahub.objects.count(), 1)
        self.assertIsNone(RegistrationDataImportDatahub.objects.filter(id=self.rdi_datahub.id).first())
        self.assertIsNotNone(RegistrationDataImportDatahub.objects.filter(id=self.rdi_datahub_other.id).first())

        self.assertEqual(Household.objects.count(), 1)
        self.assertIsNone(Household.objects.filter(id=self.household.id).first())
        self.assertIsNotNone(Household.objects.filter(id=self.household_other.id).first())

        self.assertEqual(Individual.objects.count(), 2)
        self.assertIsNone(Individual.objects.filter(id=self.individuals[0].id).first())
        self.assertIsNotNone(Individual.objects.filter(id=self.individuals_other[0].id).first())

        self.assertEqual(Document.objects.count(), 0)
        self.assertIsNone(Document.objects.filter(id=self.document.id).first())
