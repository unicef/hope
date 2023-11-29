from unittest.mock import patch

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.grievance.fixtures import TicketNeedsAdjudicationDetailsFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory

FILTER_GRIEVANCE_BY_CROSS_AREA = """
query AllGrievanceTickets($isCrossArea: Boolean) {
  allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", isCrossArea: $isCrossArea) {
    edges {
      node {
        status
        category
        admin
        language
        description
        consent
      }
    }
  }
}
"""


@patch("hct_mis_api.apps.core.es_filters.ElasticSearchFilterSet.USE_ALL_FIELDS_AS_POSTGRES_DB", True)
class TestCrossAreaFilterAvailable(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(partner=partner_unicef)

        admin_area1 = AreaFactory()
        admin_area2 = AreaFactory()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        individual1_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        individual2_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        household1_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=admin_area1, head_of_household=individual1_from_area1
        )
        individual1_from_area1.household = household1_from_area1
        individual1_from_area1.save()
        household2_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=admin_area1, head_of_household=individual2_from_area1
        )
        individual2_from_area1.household = household2_from_area1
        individual2_from_area1.save()

        individual_from_area2 = IndividualFactory(business_area=cls.business_area, household=None)
        household_from_area2 = HouseholdFactory(
            business_area=cls.business_area, admin2=admin_area2, head_of_household=individual_from_area2
        )
        individual_from_area2.household = household_from_area2
        individual_from_area2.save()

        cls.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=GrievanceTicket.objects.create(
                **{
                    "business_area": cls.business_area,
                    "language": "Polish",
                    "consent": True,
                    "description": "Cross Area Grievance",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
        )
        cls.needs_adjudication_ticket_cross_area.possible_duplicates.set([individual_from_area2])
        cls.needs_adjudication_ticket_cross_area.populate_cross_area_flag()

        cls.needs_adjudication_ticket_same_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=GrievanceTicket.objects.create(
                **{
                    "business_area": cls.business_area,
                    "language": "Polish",
                    "consent": True,
                    "description": "Same Area Grievance",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
        )
        cls.needs_adjudication_ticket_same_area.possible_duplicates.set([individual2_from_area1])
        cls.needs_adjudication_ticket_same_area.populate_cross_area_flag()

    def test_cross_area_filter_true(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.needs_adjudication_ticket_cross_area.refresh_from_db()
        self.needs_adjudication_ticket_same_area.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_cross_area.is_cross_area, True)
        self.assertEqual(self.needs_adjudication_ticket_same_area.is_cross_area, False)

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={"user": self.user},
            variables={"isCrossArea": True},
        )

    def test_without_cross_area_filter(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={"user": self.user},
            variables={"isCrossArea": None},
        )
