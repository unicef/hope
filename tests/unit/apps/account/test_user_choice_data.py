from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan


class RoleAssignmentsTest(APITestCase):
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
        super().setUpTestData()
        cls.business_area = create_afghanistan()

        Partner.objects.get_or_create(name="UNHCR")
        Partner.objects.get_or_create(name="WFP")

        # UNICEF partner
        partner_unicef, _ = Partner.objects.get_or_create(name="UNICEF")

        # UNICEF subpartner
        unicef_afghanistan = PartnerFactory(name="UNICEF Partner in Afghanistan", parent=partner_unicef)
        cls.user = UserFactory(partner=unicef_afghanistan, username="unicef_user")

        # partner with role in BA
        partner_with_role = PartnerFactory(name="Partner with BA access")

        # partner with role in BA but is a parent
        parent_partner = PartnerFactory(name="Parent Partner with BA access")
        partner_with_role.parent = parent_partner
        partner_with_role.save()

        for partner in Partner.objects.all():
            partner.allowed_business_areas.add(cls.business_area)
            cls.create_partner_role_with_permissions(partner, [], cls.business_area)

        # partner allowed in BA but without role -> listed anyway
        partner_without_role = PartnerFactory(name="Partner Without Role")
        partner_without_role.allowed_business_areas.add(cls.business_area)

        # partner not allowed in BA -> not listed
        PartnerFactory(name="Partner Not Allowed in BA")

    def test_user_choice_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.USER_CHOICE_DATA_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
