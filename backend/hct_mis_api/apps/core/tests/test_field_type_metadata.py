from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestMetaDataFilterType(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # graph query to be called.
        cls.user = UserFactory.create()
        cls.CORE_FLEX_META_TYPE_QUERY = """
        query AllFields {
          allCoreFieldAttributes {
            id
            name
            label
            hint
            required
            associatedWith
            type
            choices {
              name
              label
            }
          }
          allFlexFieldAttributes {
            id
            name
            label
            hint
            required
            associatedWith
            choices {
              name
              label
            }
          }
        }
        """

    def test_core_meta_type_query(self):
        self.snapshot_graphql_request(
            request_string=self.CORE_FLEX_META_TYPE_QUERY,
            context={"user": self.user},
        )
