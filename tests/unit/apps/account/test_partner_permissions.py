import pytest
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import (AdminAreaLimitedTo, Role,
                                             RoleAssignment, User)
from hct_mis_api.apps.account.permissions import Permissions
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
        cls.other_partner.allowed_business_areas.add(cls.business_area)
        RoleAssignment.objects.create(
            business_area=cls.business_area,
            program=cls.program,
            partner=cls.other_partner,
            role=cls.role_2,
        )
        area_limits = AdminAreaLimitedTo.objects.create(partner=cls.other_partner, program=cls.program)
        area_limits.areas.add(cls.area_1)

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.unicef_partner)

        cls.unicef_user = UserFactory(partner=cls.unicef_hq)

        RoleAssignment.objects.create(
            business_area=cls.business_area,
            user=cls.other_user,
            role=cls.role_1,
            program=None,
        )

        role_with_all_permissions = Role.objects.get_or_create(name="Role with all permissions")[0]
        role_with_all_permissions.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
        role_with_all_permissions.save()  # UNICEF HQ has role with all permissions

    @pytest.fixture(autouse=True)  # Override fixture because the initial data has old format that is invalid now
    def create_unicef_partner(self) -> None:
        return

    def test_partner_is_unicef(self) -> None:
        self.assertTrue(self.unicef_partner.is_unicef)
        self.assertFalse(self.other_partner.is_unicef)

    def test_partner_is_unicef_subpartner(self) -> None:
        self.assertTrue(self.unicef_hq.is_unicef_subpartner)
        self.assertFalse(self.other_partner.is_unicef_subpartner)

    def test_get_partner_program_ids_for_business_area(self) -> None:
        resp_1 = self.other_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)

        self.assertListEqual(resp_1, [str(self.program.pk)])

        resp_2 = self.unicef_user.partner.get_program_ids_for_business_area(business_area_id=self.business_area.pk)
        self.assertListEqual(resp_2, [str(self.program.pk)])

    def test_get_partner_program_ids_for_permission_in_business_area(self) -> None:
        resp_1 = self.other_user.partner.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE],
        )
        self.assertListEqual(resp_1, [])

        resp_2 = self.other_user.partner.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE, Permissions.PROGRAMME_FINISH],
        )

        self.assertListEqual(resp_2, [str(self.program.pk)])

        resp_3 = self.unicef_user.partner.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE],
        )
        self.assertListEqual(resp_3, [str(self.program.pk)])

    def test_get_user_program_ids_for_permission_in_business_area(self) -> None:
        program_other = ProgramFactory.create(status=Program.DRAFT, business_area=self.business_area)
        resp_1 = self.other_user.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE],
        )
        # user has role_1 for program=None
        self.assertIn(str(self.program.pk), resp_1)
        self.assertIn(str(program_other.pk), resp_1)

        resp_2 = self.other_user.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE, Permissions.PROGRAMME_FINISH],
        )
        self.assertIn(str(self.program.pk), resp_2)
        self.assertIn(str(program_other.pk), resp_2)

        resp_3 = self.unicef_user.get_program_ids_for_permissions_in_business_area(
            business_area_id=self.business_area.pk,
            permissions=[Permissions.PROGRAMME_CREATE],
        )
        self.assertIn(str(self.program.pk), resp_3)
        self.assertIn(str(program_other.pk), resp_3)

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
        # two roles with program
        role_1_program = User.permissions_in_business_area(
            self.other_user, business_area_slug=self.business_area.slug, program_id=self.program.pk
        )
        for role in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
            self.assertTrue(role in role_1_program)

        # one role with different program
        another_program = ProgramFactory.create(status=Program.DRAFT, business_area=self.business_area)
        role_1_another_program = User.permissions_in_business_area(
            self.other_user, business_area_slug=self.business_area.slug, program_id=another_program.pk
        )
        self.assertTrue("PROGRAMME_CREATE" in role_1_another_program)

        role_unicef = User.permissions_in_business_area(self.unicef_user, business_area_slug=self.business_area.slug)
        for role in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
            self.assertTrue(role in role_unicef)
        self.assertEqual(self.unicef_user.partner.role_assignments.count(), 1)
        self.assertEqual(
            self.unicef_user.partner.role_assignments.first().role, Role.objects.get(name="Role with all permissions")
        )

        role_unicef_program = User.permissions_in_business_area(
            self.unicef_user, business_area_slug=self.business_area.slug, program_id=self.program.pk
        )
        for role in ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]:
            self.assertTrue(role in role_unicef_program)

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
        self.assertTrue(user_with_partner_role_and_program_access)  # role on user is for program=None
        user_with_partner_role_and_program_access = User.has_perm(self.other_user, "PROGRAMME_FINISH", self.program)
        self.assertTrue(user_with_partner_role_and_program_access)  # role on partner is for program=self.program

        # check perms wrong program_id
        another_program = ProgramFactory.create(status=Program.DRAFT, business_area=self.business_area)
        user_with_access = User.has_perm(self.other_user, "PROGRAMME_CREATE", another_program)
        self.assertTrue(user_with_access)  # role on user is for program=None
        user_without_access = User.has_perm(self.other_user, "PROGRAMME_FINISH", another_program)
        self.assertFalse(user_without_access)

        # check with program_id user partner is_unicef
        self.assertTrue(User.has_perm(self.unicef_user, "PROGRAMME_FINISH", self.program))
        self.assertTrue(User.has_perm(self.unicef_user, "PROGRAMME_CREATE", self.program))
