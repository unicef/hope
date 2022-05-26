from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household

from hct_mis_api.apps.program.fixtures import ProgramFactory


class GoldenRecordTargetingCriteriaFitRangeQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter(
        $targetingCriteria: TargetingCriteriaObjectType!
        $program: ID!
        $businessArea: String
        $criteriaFitRange: [Int]
    ) {
      goldenRecordByTargetingCriteria(
        targetingCriteria: $targetingCriteria
        program: $program
        businessArea: $businessArea
        excludedIds: "",
        criteriaFitRange: $criteriaFitRange
    ) {
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

        household, individuals = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"birth_date": "1990-01-01", "phone_no": "1234567890"}
        )

        household, individuals = create_household(
            {"size": 2, "business_area": cls.business_area},
            {"birth_date": "1990-01-01", "phone_no": "1234567890"}
        )

        household, individuals = create_household(
            {"size": 3, "business_area": cls.business_area},
            {"birth_date": "1990-01-01", "phone_no": "1234567890"}
        )

    @parameterized.expand(
        [
            ([1, 1], ),
            ([2, 2], ),
            ([3, 3], ),
            ([1, 3], ),
            ([2, 3], ),
        ]
    )
    def test_filter_records_by_fit_range(self, fit_range):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_VIEW_DETAILS], self.business_area)
        variables = {
            "program": self.id_to_base64(self.program.id, "Program"),
            "businessArea": self.business_area.slug,
            "criteriaFitRange": fit_range,
            "targetingCriteria": {
                "rules": [
                    {
                        "filters": [],
                        "individualsFiltersBlocks": [
                            {
                                "individualBlockFilters": [
                                    {
                                        "comparisionMethod": "RANGE",
                                        "arguments": [
                                            20,
                                            41
                                        ],
                                        "fieldName": "age",
                                        "isFlexField": False
                                    },
                                    {
                                        "comparisionMethod": "EQUALS",
                                        "arguments": [
                                            "True"
                                        ],
                                        "fieldName": "has_phone_number",
                                        "isFlexField": False
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        self.snapshot_graphql_request(request_string=self.QUERY, context={"user": self.user}, variables={**variables})

    def test_filter_records_raises_error_when_min_is_higher_than_max(self):
        self.create_user_role_with_permissions(self.user, [Permissions.TARGETING_VIEW_DETAILS], self.business_area)
        variables = {
            "program": self.id_to_base64(self.program.id, "Program"),
            "businessArea": self.business_area.slug,
            "criteriaFitRange": [7, 2],
            "targetingCriteria": {}
        }

        self.snapshot_graphql_request(
            request_string=self.QUERY, context={"user": self.user}, variables={**variables}
        )
