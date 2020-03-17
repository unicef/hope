from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestMetaDataFilterType(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # graph query to be called.
        cls.user = UserFactory.create()
        cls.META_DATA_FILTER_TYPE_QUERY = """
        query MetaDataFilterType {
            metaDataFilterType {
                coreFieldTypes
                flexFieldTypes
            }
        }
        """

    def test_meta_data_filter_type_query(self):
        self.snapshot_graphql_request(
            request_string=self.META_DATA_FILTER_TYPE_QUERY,
            context={"user": self.user},
        )
