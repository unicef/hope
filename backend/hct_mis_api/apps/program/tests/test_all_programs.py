from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.account.fixtures import UserFactory, BusinessAreaFactory
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestGettingAllPrograms(APITestCase):
    QUERY = """\
query AllProgramsForChoices(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $status: [String]
  $sector: [String]
  $businessArea: String!
  $search: String
  $numberOfHouseholds: String
  $budget: String
  $startDate: Date
  $endDate: Date
  $orderBy: String
) {
  allPrograms(
    before: $before
    after: $after
    first: $first
    last: $last
    status: $status
    sector: $sector
    businessArea: $businessArea
    search: $search
    numberOfHouseholds: $numberOfHouseholds
    budget: $budget
    orderBy: $orderBy
    startDate: $startDate
    endDate: $endDate
  ) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
      __typename
    }
    totalCount
    edgeCount
    edges {
      cursor
      node {
        id
        name
        totalNumberOfHouseholds
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS], cls.business_area
        )

    def test_status_choices_query(self):
        response = self.graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={
                "businessArea": self.business_area.slug,
                "status": [],
                "sector": [],
                "numberOfHouseholds": '{"min":"2","max":"3"}',
                "budget": "{}",
                "first": 5,
                "orderBy": None,
            },
        )
        assert "errors" not in response

        print("response", response)
        assert False
