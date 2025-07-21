from django.test import TestCase

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, User, UserRole
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from tests.extras.test_utils.factories.geo import AreaFactory
from hct_mis_api.apps.geo.models import Area
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class UserPartnerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.role_1 = Role.objects.create(name="Create_program", permissions=["PROGRAMME_CREATE"])
        cls.role_2 = Role.objects.create(name="Finish_program", permissions=["PROGRAMME_FINISH"])
        cls.area_1 = AreaFactory(name="Area 1", p_code="AREA1")
        cls.area_2 = AreaFactory(name="Area 2", p_code="AREA2")
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)
        cls.other_partner = PartnerFactory(name="Partner")
        ba_partner_through = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area, partner=cls.other_partner
        )
        ba_partner_through.roles.set([cls.role_2])
        program_partner_through = ProgramPartnerThrough.objects.create(program=cls.program, partner=cls.other_partner)
        program_partner_through.areas.set([cls.area_1])
        cls.other_user = UserFactory(partner=cls.other_partner)

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        program_unicef_through, _ = ProgramPartnerThrough.objects.get_or_create(
            program=cls.program, partner=cls.unicef_partner
        )
        program_unicef_through.areas.set([cls.area_1, cls.area_2])
        cls.unicef_user = UserFactory(partner=cls.unicef_partner)

        UserRole.objects.create(
            business_area=cls.business_area,
            user=cls.unicef_user,
            role=cls.role_1,
        )
        UserRole.objects.create(
            business_area=cls.business_area,
            user=cls.other_user,
            role=cls.role_1,
        )

        cls.user_without_role = UserFactory(partner=cls.unicef_partner)

    def test_partner_is_hope(self) -> None:
        self.assertTrue(self.unicef_partner.is_unicef)
        self.assertFalse(self.other_partner.is_unicef)

    def test_get_partner_program_ids_for_business_area(self) -> None:
        resp_1 = self.other_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)

        self.assertListEqual(resp_1, [str(self.program.pk)])

        resp_2 = self.unicef_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)
        self.assertListEqual(resp_2, [str(self.program.pk)])

    def test_get_partner_roles_for_business_area(self) -> None:
        empty_qs = self.other_user.partner.get_roles_for_business_area()
        self.assertQuerysetEqual(empty_qs, Role.objects.none())

        resp_1 = self.other_user.partner.get_roles_for_business_area(business_area_slug=self.business_area.slug)
        resp_2 = self.other_user.partner.get_roles_for_business_area(business_area_id=self.business_area.pk)

        self.assertQuerysetEqual(resp_1, resp_2)
        self.assertQuerysetEqual(resp_1, Role.objects.filter(pk=self.role_2.pk))

        resp_3 = self.unicef_user.partner.get_roles_for_business_area(business_area_slug=self.business_area.slug)
        self.assertQuerysetEqual(resp_3, Role.objects.none())

    def test_get_partner_areas_per_program(self) -> None:
        other_partner_areas = self.other_user.partner.get_program_areas(self.program.pk)
        self.assertQuerysetEqual(other_partner_areas, Area.objects.filter(id=self.area_1.pk))

        unicef_partner_areas = self.unicef_user.partner.get_program_areas(self.program.pk)
        self.assertQuerysetEqual(unicef_partner_areas, Area.objects.filter(id__in=[self.area_1.pk, self.area_2.pk]))

    def test_partner_permissions_in_business_area(self) -> None:
        # two roles without program
        roles_2 = User.permissions_in_business_area(self.other_user, business_area_slug=self.business_area.slug)
        for role in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
            self.assertTrue(role in roles_2)

        # one role with program
        role_1 = User.permissions_in_business_area(self.unicef_user, business_area_slug=self.business_area.slug)
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

        # one role unicef user
        roles_1_for_unicef_user = User.permissions_in_business_area(
            self.unicef_user, business_area_slug=self.business_area.slug, program_id=self.program.pk
        )
        self.assertEqual(roles_1_for_unicef_user.sort(), default_list)

        # user with unicef partner but without role in BA
        roles_0_for_unicef_user = User.permissions_in_business_area(
            self.user_without_role, business_area_slug=self.business_area.slug, program_id=self.program.pk
        )
        self.assertEqual(roles_0_for_unicef_user, list())

    def test_partner_has_permission(self) -> None:
        # check user_roles
        user_has_one_role = User.has_permission(self.unicef_user, "PROGRAMME_CREATE", self.business_area)
        self.assertTrue(user_has_one_role)

        # check user_roles
        user_without_access = User.has_permission(self.unicef_user, "Role_Not_Added", self.business_area)
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
            self.unicef_user, "PROGRAMME_FINISH", self.business_area, self.program.pk
        )
        self.assertFalse(unicef_user_without_perms)

        unicef_user_with_perms = User.has_permission(
            self.unicef_user, "PROGRAMME_CREATE", self.business_area, self.program.pk
        )
        self.assertTrue(unicef_user_with_perms)
