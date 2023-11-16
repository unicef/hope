from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class UserPartnerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.role_1 = Role.objects.create(name="Create_program", permissions=[Permissions.PROGRAMME_CREATE])
        cls.role_2 = Role.objects.create(name="Finish_program", permissions=[Permissions.PROGRAMME_FINISH])
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [str(cls.role_2.pk)],
                "programs": {str(cls.program.pk): ["admin_id_1"]},
            }
        }
        cls.other_partner = PartnerFactory(name="Partner", permissions=partner_perms)
        cls.other_user = UserFactory(partner=cls.other_partner)
        cls.is_unicef_partner = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(partner=cls.is_unicef_partner)

        UserRole.objects.create(
            business_area=cls.business_area,
            user=cls.user,
            role=cls.role_1,
        )

    def test_partner_is_hope(self) -> None:
        self.assertTrue(self.is_unicef_partner.is_unicef)
        self.assertFalse(self.other_partner.is_unicef)

    def test_get_partner_role_ids_list(self) -> None:
        empty_list = User.get_partner_role_ids_list(self.other_user)
        self.assertEqual(list(), empty_list)

        resp_1 = User.get_partner_role_ids_list(self.other_user, business_area_slug=self.business_area.slug)
        resp_2 = User.get_partner_role_ids_list(self.other_user, business_area_id=self.business_area.pk)

        self.assertListEqual(resp_1, resp_2)
        self.assertEqual(resp_1, [str(self.role_2.pk)])

        resp_3 = User.get_partner_role_ids_list(self.user, business_area_slug=self.business_area.slug)
        self.assertEqual(list(), resp_3)

    def test_get_partner_programs_areas_dict(self) -> None:
        empty_dict = User.get_partner_programs_areas_dict(self.other_user)
        self.assertEqual(dict(), empty_dict)

        resp_1 = User.get_partner_programs_areas_dict(self.other_user, business_area_slug=self.business_area.slug)
        resp_2 = User.get_partner_programs_areas_dict(self.other_user, business_area_id=self.business_area.pk)

        self.assertEqual(resp_1, resp_2)
        self.assertEqual(resp_1, {str(self.program.pk): ["admin_id_1"]})

        resp_3 = User.get_partner_programs_areas_dict(self.user, business_area_slug=self.business_area.slug)
        self.assertEqual(dict(), resp_3)

    def test_get_partner_areas_ids_per_program(self) -> None:
        empty_list = User.get_partner_areas_ids_per_program(self.user, self.business_area.pk, self.business_area.pk)
        self.assertEqual(list(), empty_list)

        resp_1 = User.get_partner_areas_ids_per_program(self.other_user, self.program.pk, self.business_area.pk)
        self.assertEqual(resp_1, ["admin_id_1"])

    # def test_partner_permissions_in_business_area(self) -> None:
    #     pass
    #
    # def test_partner_has_permission(self) -> None:
    #     pass
