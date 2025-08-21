from django.test import TestCase
from extras.test_utils.factories.core import (
    create_afghanistan,
    PeriodicFieldDataFactory,
    FlexibleAttributeForPDUFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.sanction_list import SanctionListIndividualFactory
from freezegun import freeze_time

from hope.apps.core.models import PeriodicFieldData
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.apps.household.models import FEMALE, MALE
from hope.apps.payment.models import Payment
from hope.apps.periodic_data_update.service.periodic_data_update_online_edit_generate_data_service import (
    PDUOnlineEditGenerateDataService,
)
from hope.apps.program.models import Program


class TestPDUOnlineEditGenerateDataService(TestCase):
    rdi = None
    business_area = None
    program = None

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=cls.business_area)
        cls.rdi = RegistrationDataImportFactory()
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program.pk,
                "registration_data_import": cls.rdi,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                    "registration_data_import": cls.rdi,
                },
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                    "registration_data_import": cls.rdi,
                },
            ],
        )
        muac_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=5,
            rounds_names=["January", "February", "March", "April", "May"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="muac",
            pdu_data=muac_data,
        )
        month_worked_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=5,
            rounds_names=["January", "February", "March", "April", "May"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="month worked",
            pdu_data=month_worked_data,
        )
        cls.periodic_data_update_online_Edit = PDUOnlineEditFactory(
            program=cls.program,
            business_area=cls.business_area,
        )
        cls.rounds_data= [
            {
                "field": "muac",
                "round": 2,
                "round_name": "February",
                "number_of_records": 100,
            },
            {
                "field": "month_worked",
                "round": 4,
                "round_name": "April",
                "number_of_records": 58,
            },
        ]

    def test_generate_edit_data(
        self,
    ) -> None:
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters={},
            rounds_data=self.rounds_data,
        )
        edit_data = service.generate_edit_data()

        assert edit_data == [
            {
                "individual_uuid": str(self.individuals[0].pk),
                "unicef_id": self.individuals[0].unicef_id,
                "first_name": self.individuals[0].given_name,
                "last_name": self.individuals[0].family_name,
                "pdu_fields": {
                    "muac": {
                        "round_number": 2,
                        "round_name": "February",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "month_worked": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.BOOL,
                        "is_editable": True,
                    },
                },
            },
            {
                "individual_uuid": str(self.individuals[1].pk),
                "unicef_id": self.individuals[1].unicef_id,
                "first_name": self.individuals[1].given_name,
                "last_name": self.individuals[1].family_name,
                "pdu_fields": {
                    "muac": {
                        "round_number": 2,
                        "round_name": "February",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "month_worked": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.BOOL,
                        "is_editable": True,
                    },
                },
            }
        ]
        assert len(edit_data) == 2

    def test_generate_edit_data_with_one_value_already_set(self) -> None:
        individual = self.individuals[0]
        individual.flex_fields = {
            "muac": {
                "2": {
                    "value": 20,
                    "collection_date": "2021-05-01",
                }
            }
        }
        individual.save()
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters={},
            rounds_data=self.rounds_data,
        )
        edit_data = service.generate_edit_data()

        assert edit_data == [
            {
                "individual_uuid": str(individual.pk),
                "unicef_id": individual.unicef_id,
                "first_name": individual.given_name,
                "last_name": individual.family_name,
                "pdu_fields": {
                    "muac": {
                        "round_number": 2,
                        "round_name": "February",
                        "value": 20,  # value is already set
                        "collection_date": None, # collection date is not needed as the value will not be edited
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": False,
                    },
                    "month_worked": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.BOOL,
                        "is_editable": True,
                    },
                },
            },
            {
                "individual_uuid": str(self.individuals[1].pk),
                "unicef_id": self.individuals[1].unicef_id,
                "first_name": self.individuals[1].given_name,
                "last_name": self.individuals[1].family_name,
                "pdu_fields": {
                    "muac": {
                        "round_number": 2,
                        "round_name": "February",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "month_worked": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.BOOL,
                        "is_editable": True,
                    },
                },
            }
        ]
        assert len(edit_data) == 2

    def test_generate_edit_data_exclude_individual_with_all_values_set(self) -> None:
        individual = self.individuals[0]
        individual.flex_fields = {
            "muac": {
                "2": {
                    "value": 20,
                    "collection_date": "2021-05-01",
                }
            },
            "month_worked": {
                "4": {
                    "value": 20,
                    "collection_date": "2021-04-01",
                }
            },
        }
        individual.save()
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters={},
            rounds_data=self.rounds_data,
        )
        edit_data = service.generate_edit_data()
        assert edit_data == [  # Only the second individual should be included
            {
                "individual_uuid": str(self.individuals[1].pk),
                "unicef_id": self.individuals[1].unicef_id,
                "first_name": self.individuals[1].given_name,
                "last_name": self.individuals[1].family_name,
                "pdu_fields": {
                    "muac": {
                        "round_number": 2,
                        "round_name": "February",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "month_worked": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.BOOL,
                        "is_editable": True,
                    },
                },
            }
        ]
        assert len(edit_data) == 1

    def test_get_individuals_queryset_registration_data_import_id_filter(self) -> None:
        rdi1 = RegistrationDataImportFactory()
        individual = self.individuals[0]
        individual.registration_data_import = rdi1
        individual.save()
        filters = {"registration_data_import_id": str(rdi1.pk)}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual

    def test_get_individuals_queryset_target_population_id_filter(self) -> None:
        create_household_and_individuals(
            household_data={
                "business_area": self.business_area,
                "program_id": self.program.pk,
                "registration_data_import": self.rdi,
            },
            individuals_data=[
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
            ],
        )
        pp = PaymentPlanFactory()
        PaymentFactory(parent=pp, household=self.household)
        filters = {"target_population_id": str(pp.pk)}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == set(self.individuals)

    def test_get_individuals_queryset_gender_filter(self) -> None:
        male = self.individuals[0]
        female = self.individuals[1]
        male.sex = MALE
        female.sex = FEMALE
        male.save()
        female.save()
        filters = {"gender": FEMALE}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == female

    @freeze_time("2024-07-12")
    def test_get_individuals_queryset_age_filter(self) -> None:
        individual32yo = self.individuals[0]
        individual29yo = self.individuals[1]
        individual32yo.birth_date = "1991-10-16"
        individual29yo.birth_date = "1994-10-16"
        individual32yo.save()
        individual29yo.save()
        filters = {"age": {"from": 30, "to": 32}}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual32yo

    def test_get_individuals_queryset_registration_date_filter(self) -> None:
        individual2023 = self.individuals[0]
        individual2020 = self.individuals[1]
        individual2023.first_registration_date = "2023-10-16"
        individual2020.first_registration_date = "2020-10-16"
        individual2023.save()
        individual2020.save()
        filters = {"registration_date": {"from": "2023-10-16", "to": "2023-10-16"}}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual2023

    def test_get_individuals_queryset_admin_filter(self) -> None:
        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area1a = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1a")
        area2a = AreaFactory(
            name="City Test2",
            area_type=area_type_level_2,
            p_code="area2a",
            parent=area1a,
        )
        area1b = AreaFactory(name="City Test1b", area_type=area_type_level_1, p_code="area1b")
        area2b = AreaFactory(
            name="City Test2b",
            area_type=area_type_level_2,
            p_code="area2b",
            parent=area1b,
        )
        create_household_and_individuals(
            household_data={
                "business_area": self.business_area,
                "program_id": self.program.pk,
                "registration_data_import": self.rdi,
                "admin1": area1b,
                "admin2": area2b,
            },
            individuals_data=[
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
            ],
        )
        self.household.admin1 = area1a
        self.household.save()
        filters = {"admin1": [str(area1a.pk)]}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == set(self.individuals)

        self.household.admin2 = area2a
        self.household.save()
        filters = {"admin2": [str(area2a.pk)]}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == set(self.individuals)

    def test_get_individuals_queryset_has_grievance_ticket_referral_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_REFERRAL,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketReferralDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_referral_exclude_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        individual_without_ticket = self.individuals[1]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_REFERRAL,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketReferralDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": False}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_without_ticket

    def test_get_individuals_queryset_has_grievance_ticket_negative_feedback_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketNegativeFeedbackDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_positive_feedback_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketPositiveFeedbackDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_needs_adjudication_filter(
        self,
    ) -> None:
        create_household_and_individuals(
            household_data={
                "business_area": self.business_area,
                "program_id": self.program.pk,
                "registration_data_import": self.rdi,
            },
            individuals_data=[
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
            ],
        )
        individual_with_ticket = self.individuals[0]
        possible_duplicate = self.individuals[1]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        )
        details = TicketNeedsAdjudicationDetails.objects.create(
            ticket=grievance, golden_records_individual_id=individual_with_ticket.pk
        )
        details.possible_duplicates.add(possible_duplicate)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == {individual_with_ticket, possible_duplicate}

    def test_get_individuals_queryset_has_grievance_ticket_system_flagging_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            status=GrievanceTicket.STATUS_NEW,
        )
        sanction_list_individual = SanctionListIndividualFactory()
        TicketSystemFlaggingDetails.objects.create(
            ticket=grievance,
            golden_records_individual_id=individual_with_ticket.pk,
            sanction_list_individual=sanction_list_individual,
        )
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_delete_individual_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketDeleteIndividualDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_individual_data_update_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            status=GrievanceTicket.STATUS_NEW,
        )
        TicketIndividualDataUpdateDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_sensitive_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            status=GrievanceTicket.STATUS_NEW,
            issue_type=GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST,
        )
        TicketSensitiveDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_has_grievance_ticket_complaint_filter(
        self,
    ) -> None:
        individual_with_ticket = self.individuals[0]
        grievance = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        )
        TicketComplaintDetails.objects.create(ticket=grievance, individual_id=individual_with_ticket.pk)
        filters = {"has_grievance_ticket": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 1
        assert queryset.first() == individual_with_ticket

    def test_get_individuals_queryset_received_assistance_filter(self) -> None:
        (
            household_without_payment,
            individuals_without_payment,
        ) = create_household_and_individuals(
            household_data={
                "business_area": self.business_area,
                "program_id": self.program.pk,
                "registration_data_import": self.rdi,
            },
            individuals_data=[
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
                {
                    "business_area": self.business_area,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
            ],
        )
        PaymentFactory(household=self.household, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
        filters = {"received_assistance": True}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == set(self.individuals)

        filters = {"received_assistance": False}
        service = PDUOnlineEditGenerateDataService(
            program=self.program,
            filters=filters,
            rounds_data=self.rounds_data,
        )
        queryset = service._get_individuals_queryset()
        assert queryset.count() == 2
        assert set(queryset) == set(individuals_without_payment)
