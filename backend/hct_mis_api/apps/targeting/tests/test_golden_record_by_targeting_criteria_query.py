from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory


class GoldenRecordTargetingCriteriaQueryTestCase(APITestCase):
    QUERY = """
    query GoldenRecordFilter($targetingCriteria: TargetingCriteriaObjectType!, $program: ID!, $businessArea: String) {
      goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria, program: $program, businessArea: $businessArea, excludedIds: "") {
        totalCount
        edges {
          node {
            size
            residenceStatus
          }
        }
      }
    }
    """
    FAMILY_SIZE_2_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {"comparisionMethod": "EQUALS", "arguments": [2], "fieldName": "size", "isFlexField": False}
                    ]
                }
            ]
        },
    }

    RESIDENCE_STATUS_REFUGEE_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "EQUALS",
                            "arguments": ["REFUGEE"],
                            "fieldName": "residence_status",
                            "isFlexField": False,
                        }
                    ]
                }
            ]
        }
    }
    FLEX_FIELD_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "EQUALS",
                            "arguments": ["0"],
                            "fieldName": "unaccompanied_child_h_f",
                            "isFlexField": True,
                        }
                    ]
                }
            ]
        },
        "first": 10,
    }

    SELECT_MANY_VARIABLES = {
        "targetingCriteria": {
            "rules": [
                {
                    "filters": [
                        {
                            "comparisionMethod": "CONTAINS",
                            "arguments": ["other_public", "pharmacy", "other_private"],
                            "fieldName": "treatment_facility_h_f",
                            "isFlexField": True,
                        }
                    ]
                }
            ]
        }
    }

    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.business_area = BusinessArea.objects.first()
        cls.user = UserFactory.create()
        program = ProgramFactory(business_area=cls.business_area, individual_data_needed=True)
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.household_size_1 = household
        cls.household_residence_status_citizen = cls.household_size_1

        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area},
        )
        cls.household_residence_status_refugee = household
        cls.household_size_2 = cls.household_residence_status_refugee
        cls.variables = {"program": cls.id_to_base64(program.id, "Program"), "businessArea": cls.business_area.slug}

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_golden_record_by_targeting_criteria_size(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={**self.variables, **GoldenRecordTargetingCriteriaQueryTestCase.FAMILY_SIZE_2_VARIABLES},
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_golden_record_by_targeting_criteria_residence_status(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={
                **self.variables,
                **GoldenRecordTargetingCriteriaQueryTestCase.RESIDENCE_STATUS_REFUGEE_VARIABLES,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_golden_record_by_targeting_criteria_flex_field(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={**self.variables, **GoldenRecordTargetingCriteriaQueryTestCase.FLEX_FIELD_VARIABLES},
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.TARGETING_VIEW_DETAILS],
            ),
            ("without_permission", []),
        ]
    )
    def test_golden_record_by_targeting_criteria_select_many(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=GoldenRecordTargetingCriteriaQueryTestCase.QUERY,
            context={"user": self.user},
            variables={**self.variables, **GoldenRecordTargetingCriteriaQueryTestCase.SELECT_MANY_VARIABLES},
        )
