from django.test import TestCase

from hct_mis_api.apps.account.fixtures import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import Role, RoleAssignment, User
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
        cls.other_user = UserFactory(partner=cls.other_partner)
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            program=cls.program,
            partner=cls.other_partner,
            role=cls.role_2,
        )
        AdminAreaLimitedToFactory.objects.create(partner=cls.other_partner, program=cls.program, areas=[cls.area_1])

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.unicef_partner)
        cls.unicef_user = UserFactory(partner=cls.unicef_hq)
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            program=cls.program,
            partner=cls.unicef_hq,
            role=cls.role_1,
        )

        RoleAssignment.objects.create(
            business_area=cls.business_area,
            user=cls.other_user,
            role=cls.role_1,
        )

        cls.user_without_role = UserFactory(partner=cls.unicef_hq)

    def test_partner_is_unicef(self) -> None:
        self.assertTrue(self.unicef_partner.is_unicef)
        self.assertFalse(self.other_partner.is_unicef)

    def test_partner_is_unicef_subpartner(self) -> None:
        self.assertTrue(self.unicef_partner.is_unicef_subpartner)
        self.assertFalse(self.other_partner.is_unicef_subpartner)

    def test_get_partner_program_ids_for_business_area(self) -> None:
        resp_1 = self.other_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)

        self.assertListEqual(resp_1, [str(self.program.pk)])

        resp_2 = self.unicef_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)
        self.assertListEqual(resp_2, [str(self.program.pk)])

    def test_get_partner_area_limits_per_program(self) -> None:
        other_partner_areas = self.other_user.partner.get_area_limits_for_program(self.program.pk)
        self.assertQuerysetEqual(other_partner_areas, Area.objects.filter(id=self.area_1.pk))

    def test_has_area_access(self) -> None:
        self.assertTrue(self.other_user.partner.has_area_access(self.area_1.pk, self.program.pk))
        self.assertFalse(self.other_user.partner.has_area_access(self.area_2.pk, self.program.pk))

        self.assertTrue(self.unicef_user.partner.has_area_access(self.area_1.pk, self.program.pk))
        self.assertTrue(self.unicef_user.partner.has_area_access(self.area_2.pk, self.program.pk))

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
            self.other_user, business_area_slug=self.business_area.slug, program_id=self.program.pk
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
        user_has_one_role = User.has_perm(self.unicef_user, "PROGRAMME_CREATE", self.business_area)
        self.assertTrue(user_has_one_role)

        # check user_roles
        user_without_access = User.has_perm(self.unicef_user, "Role_Not_Added", self.business_area)
        self.assertFalse(user_without_access)

        # check partner_roles
        user_with_partner_role = User.has_perm(self.other_user, "PROGRAMME_FINISH", self.business_area)
        self.assertTrue(user_with_partner_role)
        # check user_roles and partner_roles
        user_with_partner_role = User.has_perm(self.other_user, "PROGRAMME_CREATE", self.business_area)
        self.assertTrue(user_with_partner_role)

        # check user_roles and partner_roles with program_id
        user_with_partner_role_and_program_access = User.has_perm(self.other_user, "PROGRAMME_CREATE", self.program)
        self.assertTrue(user_with_partner_role_and_program_access)
        user_with_partner_role_and_program_access = User.has_perm(self.other_user, "PROGRAMME_FINISH", self.program)
        self.assertTrue(user_with_partner_role_and_program_access)

        # check perms wrong program_id
        user_without_access = User.has_perm(self.other_user, "PROGRAMME_FINISH", self.business_area)
        self.assertFalse(user_without_access)

        # check with program_id user partner is_unicef
        unicef_user_without_perms = User.has_perm(self.unicef_user, "PROGRAMME_FINISH", self.program)
        self.assertFalse(unicef_user_without_perms)

        unicef_user_with_perms = User.has_perm(self.unicef_user, "PROGRAMME_CREATE", self.program)
        self.assertTrue(unicef_user_with_perms)
