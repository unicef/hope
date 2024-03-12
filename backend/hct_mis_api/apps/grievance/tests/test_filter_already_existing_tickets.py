from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceComplaintTicketFactory,
    GrievanceTicketFactory,
    SensitiveGrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory


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

        cls.household, cls.individuals = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        program = ProgramFactory(business_area=cls.business_area)
        cash_plan = CashPlanFactory(program=program, business_area=cls.business_area)
        cls.payment_record = PaymentRecordFactory(
            household=cls.household,
            full_name=cls.individuals[0].full_name,
            business_area=cls.business_area,
            parent=cash_plan,
            currency="PLN",
        )
        cls.payment_record2 = PaymentRecordFactory(
            household=cls.household,
            full_name=cls.individuals[0].full_name,
            business_area=cls.business_area,
            parent=cash_plan,
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
            household=cls.household,
            individual=cls.individuals[0],
            payment_obj=cls.payment_record,
            ticket=grievance_1,
        )
        SensitiveGrievanceTicketWithoutExtrasFactory(
            household=cls.household,
            individual=cls.individuals[0],
            ticket=grievance_2,
        )
        SensitiveGrievanceTicketWithoutExtrasFactory(
            household=cls.household,
            individual=cls.individuals[0],
            payment_obj=cls.payment_record2,
            ticket=grievance_3,
        )
        GrievanceComplaintTicketFactory.create_batch(5)
        SensitiveGrievanceTicketFactory.create_batch(5)

    @parameterized.expand(
        [
            (
                "with_permission",
                [
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                ],
            ),
            ("without_permission", [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE]),
        ]
    )
    def test_filter_existing_tickets_by_payment_record(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household.id,
                "individual": self.individuals[0].id,
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
                "household": self.household.id,
                "individual": self.individuals[0].id,
                "paymentRecord": [self.payment_record.id, self.payment_record2.id],
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                ],
            ),
            ("without_permission", [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE]),
        ]
    )
    def test_filter_existing_tickets_by_household(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "household": self.household.id,
                "individual": self.individuals[0].id,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                ],
            ),
            ("without_permission", [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE]),
        ]
    )
    def test_filter_existing_tickets_by_individual(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
                "issueType": str(self.ticket.ticket.issue_type),
                "individual": self.individuals[0].id,
            },
        )
