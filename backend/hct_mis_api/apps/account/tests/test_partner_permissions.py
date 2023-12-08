from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class UserPartnerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.role_1 = Role.objects.create(name="Create_program", permissions=["PROGRAMME_CREATE"])
        cls.role_2 = Role.objects.create(name="Finish_program", permissions=["PROGRAMME_FINISH"])
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
        UserRole.objects.create(
            business_area=cls.business_area,
            user=cls.other_user,
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

    def test_partner_permissions_in_business_area(self) -> None:
        # two roles without program
        roles_2 = User.permissions_in_business_area(self.other_user, business_area_slug=self.business_area.slug)
        for role in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
            self.assertTrue(role in roles_2)

        # one role with program
        role_1 = User.permissions_in_business_area(self.user, business_area_slug=self.business_area.slug)
        default_list = [
            "USER_MANAGEMENT_VIEW_LIST",
            "RDI_VIEW_DETAILS",
            "ACTIVITY_LOG_VIEW",
            "PM_VIEW_LIST",
            "PAYMENT_VERIFICATION_VIEW_DETAILS",
            "GRIEVANCES_FEEDBACK_VIEW_LIST",
            "PM_VIEW_DETAILS",
            "POPULATION_VIEW_INDIVIDUALS_LIST",
            "PROGRAMME_VIEW_LIST_AND_DETAILS",
            "PAYMENT_VERIFICATION_VIEW_LIST",
            "POPULATION_VIEW_HOUSEHOLDS_DETAILS",
            "RDI_VIEW_LIST",
            "REPORTING_EXPORT",
            "TARGETING_VIEW_LIST",
            "POPULATION_VIEW_HOUSEHOLDS_LIST",
            "POPULATION_VIEW_INDIVIDUALS_DETAILS",
            "GRIEVANCES_FEEDBACK_VIEW_DETAILS",
            "PROGRAMME_CREATE",
            "GRIEVANCES_VIEW_LIST_SENSITIVE",
            "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE",
            "GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE",
            "GRIEVANCES_VIEW_DETAILS_SENSITIVE",
            "DASHBOARD_VIEW_COUNTRY",
            "TARGETING_VIEW_DETAILS",
        ].sort()
        self.assertEqual(role_1.sort(), default_list)

        # empty list because wrong program id
        empty_list = User.permissions_in_business_area(
            self.other_user, business_area_slug=self.business_area.slug, program_id=self.business_area.pk
        )
        self.assertEqual(empty_list, list())

        # one role is_unicef user
        roles_1_for_unicef_user = User.permissions_in_business_area(
            self.user, business_area_slug=self.business_area.slug, program_id=self.program.pk
        )
        self.assertEqual(roles_1_for_unicef_user.sort(), default_list)

    def test_partner_has_permission(self) -> None:
        # check user_roles
        user_has_one_role = User.has_permission(self.user, "PROGRAMME_CREATE", self.business_area)
        self.assertTrue(user_has_one_role)

        # check user_roles
        user_without_access = User.has_permission(self.user, "Role_Not_Added", self.business_area)
        self.assertFalse(user_without_access)

        # check partner_roles
        user_with_partner_role = User.has_permission(self.other_user, "PROGRAMME_FINISH", self.business_area)
        self.assertTrue(user_with_partner_role)
        # check user_roles and partner_roles
        user_with_partner_role = User.has_permission(self.other_user, "PROGRAMME_CREATE", self.business_area)
        self.assertTrue(user_with_partner_role)

        # check user_roles and partner_roles with program_id
        user_with_partner_role_and_program_access = User.has_permission(
            self.other_user, "PROGRAMME_CREATE", self.business_area, self.program.pk
        )
        self.assertTrue(user_with_partner_role_and_program_access)
        user_with_partner_role_and_program_access = User.has_permission(
            self.other_user, "PROGRAMME_FINISH", self.business_area, self.program.pk
        )
        self.assertTrue(user_with_partner_role_and_program_access)

        # check perms wrong program_id
        user_without_access = User.has_permission(
            self.other_user, "PROGRAMME_FINISH", self.business_area, self.business_area.pk
        )
        self.assertFalse(user_without_access)

        # check with program_id user partner is_unicef
        unicef_user_without_perms = User.has_permission(
            self.user, "PROGRAMME_FINISH", self.business_area, self.program.pk
        )
        self.assertFalse(unicef_user_without_perms)

        unicef_user_with_perms = User.has_permission(self.user, "PROGRAMME_CREATE", self.business_area, self.program.pk)
        self.assertTrue(unicef_user_with_perms)
