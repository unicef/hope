from typing import Any, List

from django.core.management import call_command

import pytest
from flaky import flaky
from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceComplaintTicketFactory,
    GrievanceTicketFactory,
    SensitiveGrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


@pytest.mark.skip("Temporarily skipped")
class TestAlreadyExistingFilterTickets(APITestCase):
    FILTER_EXISTING_GRIEVANCES_QUERY = """
    query ExistingGrievanceTickets(
      $businessArea: String!,
      $category: String!,
      $issueType: String,
      $household: ID,
      $individual: ID,
      $paymentRecord: [ID]
    ) {
      existingGrievanceTickets(
        businessArea: $businessArea,
        category: $category,
        issueType: $issueType,
        household: $household,
        individual: $individual,
        paymentRecord: $paymentRecord,
        orderBy: "id"
      ) {
        edges {
          node {
            id
            category
            issueType
            sensitiveTicketDetails {
              household {
                size
              }
              individual {
                fullName
              }
              paymentRecord {
                fullName
              }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory(partner=cls.partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.household_1, cls.individuals_1 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        cls.household_2, cls.individuals_2 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "Frank", "family_name": "Sinatra", "middle_name": "", "full_name": "Frank Sinatra"},
        )
        cls.household_3, cls.individuals_3 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "Jane", "family_name": "XDoe", "middle_name": "", "full_name": "Jane XDoe"},
        )
        program = ProgramFactory(business_area=cls.business_area)
        payment_plan = PaymentPlanFactory(program_cycle=program.cycles.first(), business_area=cls.business_area)
        cls.payment = PaymentFactory(
            household=cls.household_1,
            collector=cls.individuals_1[0],
            business_area=cls.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        cls.payment2 = PaymentFactory(
            household=cls.household_2,
            collector=cls.individuals_2[0],
            business_area=cls.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        grievance_1 = GrievanceTicketFactory(
            id="0fdbf2fc-e94e-4c64-acce-6e7edd4bbd87",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        )
        grievance_2 = GrievanceTicketFactory(
            id="12398c71-81ef-4e24-964d-f77e853971ab",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        )
        grievance_3 = GrievanceTicketFactory(
            id="c98d0373-1b20-48eb-8b87-7237477ed782",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        )
        cls.ticket = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=cls.household_1,
            individual=cls.individuals_1[0],
            payment=cls.payment,
            ticket=grievance_1,
        )
        SensitiveGrievanceTicketWithoutExtrasFactory(
            household=cls.household_2,
            individual=cls.individuals_2[0],
            ticket=grievance_2,
        )
        SensitiveGrievanceTicketWithoutExtrasFactory(
            household=cls.household_3,
            individual=cls.individuals_3[0],
            payment=cls.payment_record2,
            ticket=grievance_3,
        )
        GrievanceComplaintTicketFactory.create_batch(5)
        SensitiveGrievanceTicketFactory.create_batch(5)

    @pytest.mark.skip("This test has never worked with pytest")
    def test_filter_existing_tickets_by_payment_record_with_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household_1.id,
                "individual": self.individuals_1[0].id,
                "paymentRecord": [self.payment_record.id],
            },
        )

    def test_filter_existing_tickets_by_payment_record_without_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household_1.id,
                "individual": self.individuals_1[0].id,
                "paymentRecord": [self.payment_record.id],
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    def test_filter_existing_tickets_by_two_payment_records(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household_1.id,
                "individual": self.individuals_1[0].id,
                "paymentRecord": [self.payment_record.id, self.payment_record2.id],
            },
        )

    def test_filter_existing_tickets_by_household_with_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household_2.id,
                "individual": self.individuals_2[0].id,
            },
        )

    def test_filter_existing_tickets_by_household_without_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household_3.id,
                "individual": self.individuals_3[0].id,
            },
        )

    @pytest.mark.skip(reason="This test has never worked with pytest")
    def test_filter_existing_tickets_by_individual_with_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "individual": self.individuals_2[0].id,
            },
        )

    @flaky(max_runs=3, min_passes=1)
    def test_filter_existing_tickets_by_individual_without_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "individual": self.individuals_2[0].id,
            },
        )
