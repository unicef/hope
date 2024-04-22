from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan


class UserRolesTest(APITestCase):
    USER_CHOICE_DATA_QUERY = """
    query userChoiceData {
      userPartnerChoices
      {
        name
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

        Partner.objects.get_or_create(name="UNHCR")
        Partner.objects.get_or_create(name="WFP")

        # UNICEF partner
        partner_unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        cls.user = UserFactory(partner=partner_unicef, username="unicef_user")

        # partner allowed in BA
        PartnerFactory(name="Partner with BA access")

        for partner in Partner.objects.exclude(name="UNICEF"):  # unicef partner should be available everywhere
            partner.allowed_business_areas.add(cls.business_area)

        # partner not allowed in BA
        PartnerFactory(name="Partner Without Access")

    def test_user_choice_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.USER_CHOICE_DATA_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
