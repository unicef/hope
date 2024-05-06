from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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

        # partner with BA access
        role = Role.objects.create(name="Partner role")
        program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=cls.business_area)
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [str(role.pk)],
                "programs": {str(program.pk): []},
            }
        }
        PartnerFactory(name="Partner with BA access", permissions=partner_perms)

        # partner with no BA access
        partner_no_perms = {}
        PartnerFactory(name="Partner Without Access", permissions=partner_no_perms)

        for partner in Partner.objects.exclude(name="UNICEF"):  # unicef partner should be available everywhere
            partner.allowed_business_areas.add(cls.business_area)

    def test_user_choice_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.USER_CHOICE_DATA_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
