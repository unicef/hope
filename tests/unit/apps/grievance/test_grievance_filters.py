from datetime import datetime
from typing import Any, Callable

from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    URGENCY_URGENT,
    URGENCY_VERY_URGENT,
)
from hct_mis_api.apps.grievance.fixtures import TicketPaymentVerificationDetailsFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory

pytestmark = pytest.mark.django_db()


class TestGrievanceTicketFilters:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Callable) -> None:
        self.afghanistan = create_afghanistan()
        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.FINISHED,
            name="program afghanistan 2",
        )

        self.list_global_url = reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.list_url = reverse(
            "api:grievance:grievance-tickets-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_afghanistan1.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, id="45e3ffde-6a75-4799-a036-e2b00b93e94a")
        self.user2 = UserFactory(partner=self.partner, id="a6f4652c-7ade-4b51-b1f2-0d28cfc08346")
        self.api_client = api_client(self.user)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        self.country = CountryFactory()
        self.admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(
            parent=None, p_code="AF01", area_type=self.admin_type, id="d19f0e24-a411-4f0e-9404-3d54b5a5c578"
        )
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=self.admin_type)
        self.area2_2 = AreaFactory(parent=None, p_code="AF010101", area_type=self.admin_type)
        self.area_other = AreaFactory(parent=None, p_code="AF02", area_type=self.admin_type)

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[
                {
                    "preferred_language": "pl",
                    "full_name": "Tom Smith",
                },
                {
                    "preferred_language": "pl",
                },
            ],
        )
        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "id": "7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe1",
                "admin1": self.area1,
                "admin2": self.area2_2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[
                {
                    "id": "b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6",
                    "preferred_language": "en",
                },
                {
                    "preferred_language": "en",
                },
            ],
        )

        self.household1.unicef_id = "HH-0001"
        self.individuals2[0].unicef_id = "IND-0002"
        self.household1.save()
        self.individuals2[0].save()

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Needs Adjudication ticket, not cross area, program1",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                    "priority": PRIORITY_HIGH,
                    "urgency": URGENCY_URGENT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2_2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Needs Adjudication ticket, cross area, program1",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                    "priority": PRIORITY_MEDIUM,
                    "urgency": URGENCY_URGENT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Payment Verification ticket 1, program1",
                    "category": GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Payment Verification ticket 2, program2",
                    "category": GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Complaint ticket, program1",
                    "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Data Change ticket, program2",
                    "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": self.user2,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
                    "urgency": URGENCY_VERY_URGENT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "English",
                    "consent": True,
                    "description": "Sensitive ticket, program1",
                    "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Sensitive ticket, program2",
                    "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user2,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_HARASSMENT,
                    "priority": PRIORITY_MEDIUM,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area1,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "System Flagging ticket, program1",
                    "category": GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                }
            ),
        )
        self.grievance_tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)
        created_at_dates_to_set = [
            timezone.make_aware(datetime(year=2020, month=3, day=12)),
            timezone.make_aware(datetime(year=2020, month=3, day=13)),
            timezone.make_aware(datetime(year=2020, month=3, day=14)),
            timezone.make_aware(datetime(year=2020, month=7, day=12)),
            timezone.make_aware(datetime(year=2020, month=8, day=22)),
            timezone.make_aware(datetime(year=2020, month=8, day=23)),
            timezone.make_aware(datetime(year=2020, month=8, day=24)),
            timezone.make_aware(datetime(year=2020, month=8, day=25)),
            timezone.make_aware(datetime(year=2020, month=8, day=26)),
        ]
        for ticket, date in zip(self.grievance_tickets, created_at_dates_to_set):
            ticket.created_at = date
            ticket.save(update_fields=("created_at",))

        DocumentFactory(
            document_number="111222333",
            type=DocumentTypeFactory(key="birth_certificate"),
            individual=self.individuals1[0],
        )
        DocumentFactory(
            document_number="55555555",
            type=DocumentTypeFactory(key="drivers_license"),
            individual=self.individuals1[0],
        )
        DocumentFactory(
            document_number="55555555",
            type=DocumentTypeFactory(key="birth_certificate"),
            individual=self.individuals2[0],
        )
        DocumentFactory(
            document_number="111222333",
            type=DocumentTypeFactory(key="drivers_license"),
            individual=self.individuals2[0],
        )

        self.needs_adjudication_ticket_not_cross_area = TicketNeedsAdjudicationDetails.objects.create(
            ticket=self.grievance_tickets[0],
            golden_records_individual=self.individuals1[0],
            possible_duplicate=self.individuals1[1],
            score_min=100,
            score_max=200,
            extra_data={
                "golden_records": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(self.individuals1[0].pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 1.2,
                        "duplicate": False,
                        "distinct": True,
                    }
                ],
                "possible_duplicate": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(self.individuals1[1].pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 2.0,
                        "duplicate": True,
                        "distinct": False,
                    }
                ],
            },
        )
        self.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetails.objects.create(
            ticket=self.grievance_tickets[1],
            golden_records_individual=self.individuals1[0],
            possible_duplicate=self.individuals2[0],
            score_min=50,
            score_max=150,
            extra_data={
                "golden_records": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(self.individuals1[0].pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 1.2,
                        "duplicate": False,
                        "distinct": True,
                    }
                ],
                "possible_duplicate": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(self.individuals2[0].pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 2.0,
                        "duplicate": True,
                        "distinct": False,
                    }
                ],
            },
        )
        self.needs_adjudication_ticket_not_cross_area.possible_duplicates.set([self.individuals1[1]])
        self.needs_adjudication_ticket_cross_area.possible_duplicates.set([self.individuals2[0]])
        self.needs_adjudication_ticket_cross_area.populate_cross_area_flag()
        self.needs_adjudication_ticket_not_cross_area.populate_cross_area_flag()

        payment_plan = PaymentPlanFactory(
            id="689ba2ea-8ffb-4787-98e4-ae12797ee4da",
            name="TEST",
            business_area=self.afghanistan,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
        )
        self.financial_service_provider1 = FinancialServiceProviderFactory(name="Filter Value")
        payment1 = PaymentFactory(
            parent=payment_plan,
            household=self.household1,
            currency="PLN",
            financial_service_provider=self.financial_service_provider1,
        )
        payment_verification = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment1,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            received_amount=10,
        )
        self.payment_verification_ticket_1 = TicketPaymentVerificationDetailsFactory(
            ticket=self.grievance_tickets[2],
            approve_status=True,
            new_status=PaymentVerification.STATUS_RECEIVED,
            old_received_amount=0,
            new_received_amount=20,
            payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            payment_verification=payment_verification,
        )

        payment_plan2 = PaymentPlanFactory(
            name="TEST2",
            business_area=self.afghanistan,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan2)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan2, status=PaymentVerificationPlan.STATUS_ACTIVE
        )
        self.financial_service_provider2 = FinancialServiceProviderFactory(name="Value")
        payment2 = PaymentFactory(
            id="f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6",
            parent=payment_plan,
            household=self.household2,
            currency="PLN",
        )
        payment_verification = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment2,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            received_amount=10,
        )

        self.payment_verification_ticket_2 = TicketPaymentVerificationDetailsFactory(
            ticket=self.grievance_tickets[3],
            approve_status=True,
            new_status=PaymentVerification.STATUS_RECEIVED,
            old_received_amount=0,
            new_received_amount=20,
            payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            payment_verification=payment_verification,
        )

        self.complaint_ticket = TicketComplaintDetails.objects.create(
            ticket=self.grievance_tickets[4],
            household=self.household2,
            individual=self.individuals2[0],
            payment=payment2,
        )
        self.individual_data_update_ticket = TicketIndividualDataUpdateDetails.objects.create(
            ticket=self.grievance_tickets[5],
            individual=self.individuals2[0],
        )
        self.sensitive_ticket1 = TicketSensitiveDetails.objects.create(
            ticket=self.grievance_tickets[6],
            household=self.household1,
            individual=self.individuals1[0],
        )
        self.sensitive_ticket2 = TicketSensitiveDetails.objects.create(
            ticket=self.grievance_tickets[7],
            household=self.household2,
            individual=self.individuals2[0],
        )
        sanction_list_individual = SanctionListIndividualFactory(full_name="Sanction Individual")
        self.system_flagging_ticket = TicketSystemFlaggingDetails.objects.create(
            ticket=self.grievance_tickets[8],
            golden_records_individual=self.individuals2[0],
            sanction_list_individual=sanction_list_individual,
        )

        self.grievance_tickets[0].programs.add(self.program_afghanistan1)
        self.grievance_tickets[1].programs.add(self.program_afghanistan1)
        self.grievance_tickets[2].programs.add(self.program_afghanistan1)
        self.grievance_tickets[3].programs.add(self.program_afghanistan2)
        self.grievance_tickets[4].programs.add(self.program_afghanistan1)
        self.grievance_tickets[5].programs.add(self.program_afghanistan2)
        self.grievance_tickets[6].programs.add(self.program_afghanistan1)
        self.grievance_tickets[7].programs.add(self.program_afghanistan2)
        self.grievance_tickets[8].programs.add(self.program_afghanistan1)

        self.grievance_tickets[0].unicef_id = "GRV-0001"
        self.grievance_tickets[0].save()

        for grievance_ticket in self.grievance_tickets:
            grievance_ticket.refresh_from_db()

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("Filter", 1, 1),
            ("Not", 0, 0),
            ("", 6, 9),
        ],
    )
    def test_filter_by_fsp(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "fsp",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("pl", 3, 3),
            ("en", 2, 4),
            ("", 6, 9),
        ],
    )
    def test_filter_by_preferred_language(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "preferred_language",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("system", 4, 5),
            ("user", 2, 4),
            ("", 6, 9),
        ],
    )
    def test_filter_by_grievance_type(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "grievance_type",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("active", 4, 7),
            ("", 6, 9),
        ],
    )
    def test_filter_by_grievance_status(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "grievance_status",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value1, filter_value2, expected_count_for_program, expected_count_for_global",
        [
            ("drivers_license", "111222333", 2, 5),
            ("birth_certificate", "55555555", 2, 5),
            ("birth_certificate", "111222333", 4, 4),
            ("drivers_license", "55555555", 4, 4),
            ("", "111222333", 0, 0),
        ],
    )
    def test_filter_by_document_number_and_document_type(
        self,
        filter_value1: str,
        filter_value2: str,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        response_for_global = self.api_client.get(
            self.list_global_url, {"document_type": filter_value1, "document_number": filter_value2}
        )
        response_for_program = self.api_client.get(
            self.list_url, {"document_type": filter_value1, "document_number": filter_value2}
        )
        for response, expected_count in [
            (response_for_program, expected_count_for_program),
            (response_for_global, expected_count_for_global),
        ]:
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            (0, 4, 6),
            (1, 1, 1),
            (2, 1, 2),
            (3, 0, 0),
        ],
    )
    def test_filter_by_priority(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "priority",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            (0, 4, 6),
            (1, 0, 1),
            (2, 2, 2),
            (3, 0, 0),
        ],
    )
    def test_filter_by_urgency(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "urgency",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("HH-0001", 4, 4),
            ("HH-990808", 0, 0),
        ],
    )
    def test_filter_by_household_unicef_id(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "household",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe1", 1, 3),
            ("7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe2", 0, 0),
        ],
    )
    def test_filter_by_household_id(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "household_id",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6", 1, 3),
            ("b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e8", 0, 0),
        ],
    )
    def test_filter_by_individual_id(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "individual_id",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6,f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e0", 1, 1),
            ("f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e0", 0, 0),
        ],
    )
    def test_filter_by_payment_record_ids(
        self,
        filter_value: bool,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "payment_record_ids",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [(8, 2, 2), (3, 1, 2)],
    )
    def test_filter_by_category(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "category",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [(24, 2, 2), (1, 1, 1)],
    )
    def test_filter_by_issue_type(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "issue_type",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            (3, 2, 4),
            (6, 2, 2),
            ([3, 6], 4, 6),
        ],
    )
    def test_filter_by_status(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "status",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            (50, 2, 2),
            (80, 1, 1),
        ],
    )
    def test_filter_by_score_min(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "score_min",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            (200, 2, 2),
            (180, 1, 1),
        ],
    )
    def test_filter_by_score_max(
        self,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "score_max",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("d19f0e24-a411-4f0e-9404-3d54b5a5c578", 2, 4),
            ("d19f0e24-a411-4f0e-9404-3d54b5a5c579", 0, 0),
        ],
    )
    def test_filter_by_admin1(
        self,
        filter_value: str,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "admin1",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("45e3ffde-6a75-4799-a036-e2b00b93e94a", 6, 8),
            ("a6f4652c-7ade-4b51-b1f2-0d28cfc08346", 0, 1),
        ],
    )
    def test_filter_by_assigned_to(
        self,
        filter_value: str,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "assigned_to",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("689ba2ea-8ffb-4787-98e4-ae12797ee4da", 1, 1),
            ("689ba2ea-8ffb-4787-98e4-ae12797ee4d1", 0, 0),
        ],
    )
    def test_filter_by_cash_plan(
        self,
        filter_value: str,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            "cash_plan",
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "filter_expression, filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("created_at_after", "2020-07-15", 3, 5),
            ("created_at_before", "2020-07-15", 3, 4),
        ],
    )
    def test_filter_by_created_at(
        self,
        filter_expression: str,
        filter_value: int,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        self._test_filter(
            filter_expression,
            filter_value,
            expected_count_for_program,
            expected_count_for_global,
        )

    @pytest.mark.parametrize(
        "is_filtered, expected_count",
        [
            (True, 6),
            (False, 9),
        ],
    )
    def test_filter_by_program(
        self,
        is_filtered: bool,
        expected_count: int,
    ) -> None:
        filter_value = self.program_afghanistan1.slug if is_filtered else ""
        response = self.api_client.get(self.list_global_url, {"program": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "filter_value, expected_count",
        [
            (True, 6),
            (False, 3),
        ],
    )
    def test_filter_by_program_status(
        self,
        filter_value: bool,
        expected_count: int,
    ) -> None:
        response = self.api_client.get(self.list_global_url, {"is_active_program": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "has_cross_area_filter_permission, has_full_area_access, filter_value, is_filtered_for_program, is_filtered_for_global",
        [
            (False, False, False, False, False),
            (False, False, True, False, False),
            (False, True, True, False, False),
            (True, False, False, False, False),
            (True, False, True, False, True),
            (True, True, True, True, True),
        ],
    )
    def test_filter_by_cross_area(
        self,
        has_cross_area_filter_permission: list,
        has_full_area_access: int,
        filter_value: bool,
        is_filtered_for_program: bool,
        is_filtered_for_global: bool,
        create_user_role_with_permissions: Callable,
        set_admin_area_limits_in_program: Callable,
    ) -> None:
        if has_cross_area_filter_permission:
            create_user_role_with_permissions(
                user=self.user,
                permissions=[Permissions.GRIEVANCES_CROSS_AREA_FILTER],
                business_area=self.afghanistan,
                whole_business_area_access=True,
            )
        if not has_full_area_access:
            set_admin_area_limits_in_program(
                self.partner, self.program_afghanistan1, [self.area1, self.area2, self.area2_2]
            )

        response_for_program = self.api_client.get(
            self.list_url, {"is_cross_area": filter_value, "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION}
        )
        response_for_global = self.api_client.get(
            self.list_global_url,
            {"is_cross_area": filter_value, "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION},
        )

        for response, is_filtered in [
            (response_for_program, is_filtered_for_program),
            (response_for_global, is_filtered_for_global),
        ]:
            assert response.status_code == status.HTTP_200_OK
            if is_filtered:
                response_results = response.data["results"]
                assert len(response_results) == 1
                assert response_results[0]["id"] == str(self.grievance_tickets[1].id)
            else:
                response_results = response.data["results"]
                assert len(response_results) == 2
                result_ids = [result["id"] for result in response_results]
                assert str(self.grievance_tickets[0].id) in result_ids
                assert str(self.grievance_tickets[1].id) in result_ids

    def _test_filter(
        self, filter_name: str, filter_value: Any, expected_count_for_program: int, expected_count_for_global: int
    ) -> None:
        response_for_global = self.api_client.get(self.list_global_url, {filter_name: filter_value})
        response_for_program = self.api_client.get(self.list_url, {filter_name: filter_value})
        for response, expected_count in [
            (response_for_program, expected_count_for_program),
            (response_for_global, expected_count_for_global),
        ]:
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "filter_value, expected_count_for_program, expected_count_for_global",
        [
            ("GRV-0001", 1, 1),
            ("HH-0001", 4, 4),
            ("IND-0002", 2, 5),
            ("Tom", 4, 4),
            ("GRV-9918515", 0, 0),
            ("", 6, 9),
        ],
    )
    def test_search(
        self,
        filter_value: str,
        expected_count_for_program: int,
        expected_count_for_global: int,
    ) -> None:
        response_for_global = self.api_client.get(self.list_global_url, {"search": filter_value})
        response_for_program = self.api_client.get(self.list_url, {"search": filter_value})
        for response, expected_count in [
            (response_for_program, expected_count_for_program),
            (response_for_global, expected_count_for_global),
        ]:
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["results"]) == expected_count
