from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestMetaDataFilterType(APITestCase):
    QUERY = """
           query AllFieldsAttributes {
             allFieldsAttributes{
               name
               type
               labels{
                 language
                 label
               }
               labelEn
               hint
               required
               isFlexField
               associatedWith
               choices{
                 labels {
                   language
                   label
                 }
                 labelEn
                 value
               }
             }
           }
           """

    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")
        # graph query to be called.
        cls.user = UserFactory.create()

    def test_core_meta_type_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY, context={"user": self.user},
        )
