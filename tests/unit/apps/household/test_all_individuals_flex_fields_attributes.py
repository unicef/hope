from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestIndividualsFlexFieldsAttributes(APITestCase):
    QUERY = """
    query AllIndividualsFlexFieldsAttributes {
      allIndividualsFlexFieldsAttributes {
        isFlexField
        id
        type
        name
        required
        associatedWith
        labels {
          language
          label
        }
        labelEn
        hint
        choices {
          labels {
            label
            language
          }
          labelEn
          value
          admin
          listName
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(partner=cls.partner)
        cls.business_area = create_afghanistan()
        cls.program1 = ProgramFactory(name="Test program ONE", business_area=cls.business_area, status="ACTIVE")
        call_command("loadflexfieldsattributes")

    def test_all_household_flex_fields_queries_number(self) -> None:
        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        with self.assertNumQueries(2):
            self.graphql_request(
                request_string=self.QUERY,
                context={"user": self.user, "headers": headers},
                variables={},
            )
