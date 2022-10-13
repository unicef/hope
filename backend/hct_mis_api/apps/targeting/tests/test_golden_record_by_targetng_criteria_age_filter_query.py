import datetime

from dateutil.relativedelta import relativedelta
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory


class GoldenRecordTargetingCriteriaAgeFilterQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter($targetingCriteria: TargetingCriteriaObjectType!, $program: ID!, $businessArea: String) {
      goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria, program: $program, businessArea: $businessArea, excludedIds: "") {
        totalCount
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

        cls.business_area = BusinessArea.objects.first()
        cls.user = UserFactory.create()
        cls.program = ProgramFactory(business_area=cls.business_area, individual_data_needed=True)
        (household1, individuals1) = create_household({"size": 2, "business_area": cls.business_area})
        (household2, individuals2) = create_household({"size": 2, "business_area": cls.business_area})

        individuals1[0].birth_date = datetime.date.today() - relativedelta(years=+20, days=+5)  # age 20
        individuals1[1].birth_date = datetime.date.today() - relativedelta(years=+22, days=-5)  # age 21
        individuals2[0].birth_date = datetime.date.today() - relativedelta(years=+24, days=+5)  # age 24
        individuals2[1].birth_date = datetime.date.today() - relativedelta(years=+26, days=-5)  # age 25

        Individual.objects.bulk_update(individuals1 + individuals2, ["birth_date"])

    @parameterized.expand(
        [
            (
                [20],
                "LESS_THAN",
            ),
            (
                [24],
                "LESS_THAN",
            ),
            (
                [22],
                "GREATER_THAN",
            ),
            (
                [22, 26],
                "RANGE",
            ),
            (
                [21, 24],
                "RANGE",
            ),
        ]
    )
    def test_filter_records_by_age(self, arguments, method):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_VIEW_DETAILS], self.business_area)
        variables = {
            "program": self.id_to_base64(self.program.id, "Program"),
            "businessArea": self.business_area.slug,
            "targetingCriteria": {
                "rules": [
                    {
                        "filters": [],
                        "individualsFiltersBlocks": [
                            {
                                "individualBlockFilters": [
                                    {
                                        "arguments": arguments,
                                        "comparisionMethod": method,
                                        "fieldName": "age",
                                        "isFlexField": False,
                                    }
                                ]
                            }
                        ],
                    }
                ]
            },
        }

        self.snapshot_graphql_request(request_string=self.QUERY, context={"user": self.user}, variables={**variables})
