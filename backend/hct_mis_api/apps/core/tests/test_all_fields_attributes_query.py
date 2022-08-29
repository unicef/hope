from django.core.management import call_command

from parameterized import parameterized
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestMetaDataFilterType(APITestCase):
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

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
            request_string=self.QUERY,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("afghanistan",),
            ("ukraine",),
        ]
    )
    def test_rest_endpoint_all_fields_attributes(self, business_area):
        client = APIClient()
        response = client.get(reverse("fields_attributes"), data={"business_area_slug": business_area})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
