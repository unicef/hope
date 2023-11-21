from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan


class TestDataCollectionTypeSchema(APITestCase):
    QUERY_DATA_COLLECTING_TYPE_CHOICES = """
        query dataCollectionTypeChoiceData {
            dataCollectionTypeChoices {
              name
              value
            }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

        cls.data_collecting_type_full = DataCollectingTypeFactory(
            label="Full", code="full", weight=1, business_areas=[cls.business_area]
        )
        cls.data_collecting_type_partial = DataCollectingTypeFactory(
            label="Partial", code="partial", weight=2, business_areas=[cls.business_area]
        )
        cls.data_collecting_type_size_only = DataCollectingTypeFactory(
            label="Size Only", code="size_only", weight=3, business_areas=[cls.business_area]
        )
        cls.data_collecting_type_unknown = DataCollectingTypeFactory(
            label="Unknown", code="unknown", weight=4, business_areas=[cls.business_area]
        )

    def test_dct_with_unknown_code_is_not_in_list(self) -> None:  # also checks weight sorting
        self.snapshot_graphql_request(
            request_string=self.QUERY_DATA_COLLECTING_TYPE_CHOICES,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
