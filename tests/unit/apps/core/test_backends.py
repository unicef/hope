from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from unittest.mock import patch

from hct_mis_api.apps.account.fixtures import UserFactory, PartnerFactory, RoleFactory, RoleAssignmentFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.core.backends import PermissionsBackend
from django.utils import timezone


class TestPermissionsBackend(TestCase):
    def setUp(self):
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.group = Group.objects.create(name="TestGroup")
        self.permission = Permission.objects.create(codename="test_permission", name="Test Permission",
                                                    content_type_id=1)

        self.business_area = create_afghanistan()
        self.program = ProgramFactory(status=Program.ACTIVE, name="Test Program", business_area=self.business_area)

        self.role_assignment_user = RoleAssignmentFactory(
            user=self.user,
            business_area=self.business_area,
            role=None,
        )
        self.role_assignment_partner = RoleAssignmentFactory(
            partner=self.partner,
            business_area=self.business_area,
            role=None,
        )

        self.backend = PermissionsBackend()

    def test_get_all_permissions_no_cache(self):
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.test_permission", permissions)

    def test_get_all_permissions_with_cache(self):
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)

        with self.assertNumQueries(4):
            permissions = self.backend.get_all_permissions(self.user, self.business_area)
        with self.assertNumQueries(0):
            cached_permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertEqual(permissions, cached_permissions)

    @patch("hct_mis_api.api.backends.cache.get")
    def test_cache_get(self, mock_cache_get):
        mock_cache_get.return_value = {"auth.test_permission"}
        permissions = self.backend.get_all_permissions(self.user, self.business_area)
        mock_cache_get.assert_called_once_with(
            "user_permissions_version_1_1_1"
        )
        self.assertIn("auth.test_permission", permissions)

    def test_role_assignment_user_role_permissions(self):
        role = RoleFactory(name="GRIEVANCES CROSS AREA FILTER", permissions=["PROGRAMME_CREATE"])

        self.role_assignment_user.role = role
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.role_permission", permissions) # NOPE

    def test_role_assignment_user_group_permissions(self):
        self.role_assignment_user.group = self.group
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.role_permission", permissions) # NOPE

    def test_role_assignment_partner_role_permissions(self):
        role = RoleFactory(name="Test Role", permissions=["PROGRAMME_FINISH"])
        self.role_assignment_partner.role = role
        self.role_assignment_partner.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.partner_permission", permissions)  # NOPE
        
    def test_role_assignment_partner_group_permissions(self):
        self.role_assignment_partner.group = self.group
        self.role_assignment_partner.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.partner_permission", permissions)  # NOPE

    def test_has_perm_for_superuser(self):
        self.user.is_superuser = True
        self.user.save()

        self.assertTrue(self.backend.has_perm(self.user, "auth.test_permission"))

    def test_permissions_exclusion_expired_assignments(self):
        self.role_assignment_user.expiry_date = timezone.now() - timezone.timedelta(days=1)
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user)
        self.assertNotIn("auth.test_permission", permissions)

    def test_get_permissions_for_program(self):

        # Fetch permissions for the program
        permissions = self.backend.get_all_permissions(self.user, self.program)

        self.assertIn("auth.program_permission", permissions)  # NOPE

    def test_get_permissions_for_program_other(self):
        program_other = ProgramFactory(status=Program.ACTIVE, name="Test Program Other", business_area=self.business_area)

        permissions = self.backend.get_all_permissions(self.user, program_other)

        self.assertEqual(permissions, set())

    def test_get_permissions_from_all_sources(self):
        permission1 = Permission.objects.create(codename="test_permission1", name="Test Permission 1",
                                                content_type_id=1)
        permission2 = Permission.objects.create(codename="test_permission2", name="Test Permission 2",
                                                content_type_id=1)
        permission3 = Permission.objects.create(codename="test_permission3", name="Test Permission 3",
                                                content_type_id=1)
        # permission on a user group
        group_user = Group.objects.create(name="TestGroupUser")
        group_user.permissions.add(permission1)
        self.user.groups.add(self.group)

        # permission on a RoleAssignment group for user
        group_role_assignment_user = Group.objects.create(name="TestGroupRoleAssignmentUser")
        group_role_assignment_user.permissions.add(permission2)
        self.role_assignment_user.group = self.group
        self.role_assignment_user.save()

        # permission on a RoleAssignment group for partner
        group_role_assignment_partner = Group.objects.create(name="TestGroupRoleAssignmentPartner")
        group_role_assignment_partner.permissions.add(permission3)
        self.role_assignment_partner.group = self.group
        self.role_assignment_partner.save()

        # permission on a RoleAssignment role for user
        role_user = RoleFactory(name="Test Role User", permissions=["PROGRAMME_CREATE"])
        self.role_assignment_user.role = role_user
        self.role_assignment_user.save()

        # permission on a RoleAssignment role for partner
        role_partner = RoleFactory(name="Test Role Partner", permissions=["PROGRAMME_FINISH"])
        self.role_assignment_partner.role = role_partner
        self.role_assignment_partner.save()

        # all permissions
        permissions = self.backend.get_all_permissions(self.user)

        self.assertIn("auth.test_permission1", permissions)
        self.assertIn("auth.test_permission2", permissions)
        self.assertIn("auth.test_permission3", permissions)
        self.assertIn("auth.role_permission", permissions) # # NOPE

        # permissions for BA
        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("auth.test_permission1", permissions)
        self.assertIn("auth.test_permission1", permissions)
        self.assertIn("auth.test_permission2", permissions)
        self.assertIn("auth.test_permission3", permissions)
        self.assertIn("auth.role_permission", permissions) # # NOPE

        # permissions for other BA
        business_area_other = create_ukraine()
        permissions = self.backend.get_all_permissions(self.user, business_area_other)
        self.assertEqual(permissions, set())

        # permissions for program
        permissions = self.backend.get_all_permissions(self.user, self.program)
        self.assertIn("auth.test_permission1", permissions)
        self.assertIn("auth.test_permission2", permissions)
        self.assertIn("auth.test_permission3", permissions)
        self.assertIn("auth.role_permission", permissions) # # NOPE

        # permissions for other program
        program_other = ProgramFactory(status=Program.ACTIVE, name="Test Program Other", business_area=self.business_area)
        permissions = self.backend.get_all_permissions(self.user, program_other)
        self.assertEqual(permissions, set())
