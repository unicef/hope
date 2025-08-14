from typing import Any
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.core.backends import PermissionsBackend
from hope.apps.core.models import BusinessArea
from hope.apps.program.models import Program


class TestPermissionsBackend(TestCase):
    def setUp(self) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)

        self.content_type = ContentType.objects.get_for_model(BusinessArea)
        self.permission = Permission.objects.create(
            codename="test_permission", name="Test Permission", content_type=self.content_type
        )
        self.group = Group.objects.create(name="TestGroup")
        self.group.permissions.add(self.permission)

        self.business_area = create_afghanistan()
        self.program = ProgramFactory(status=Program.ACTIVE, name="Test Program", business_area=self.business_area)

        self.role_assignment_user = RoleAssignmentFactory(
            user=self.user,
            business_area=self.business_area,
            role=None,
        )
        self.partner.allowed_business_areas.add(self.business_area)
        self.role_assignment_partner = RoleAssignmentFactory(
            partner=self.partner,
            business_area=self.business_area,
            role=None,
        )

        self.backend = PermissionsBackend()

    def test_get_all_permissions_with_cache(self) -> None:
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)

        with self.assertNumQueries(4):
            permissions = self.backend.get_all_permissions(self.user, self.business_area)
        with self.assertNumQueries(0):
            cached_permissions = self.backend.get_all_permissions(self.user, self.business_area)

        assert permissions == cached_permissions

    @patch("hope.apps.core.backends.cache.get")
    def test_cache_get(self, mock_cache_get: Any) -> None:
        mock_cache_get.return_value = {self._get_permission_name_combined(self.permission)}
        permissions = self.backend.get_all_permissions(self.user, self.business_area)
        mock_cache_get.assert_called()
        assert mock_cache_get.call_count == 2
        self.assertIn(self._get_permission_name_combined(self.permission), permissions)

    def test_user_group_permissions(self) -> None:
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn(self._get_permission_name_combined(self.permission), permissions)

    def test_role_assignment_user_role_permissions(self) -> None:
        role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE", "PROGRAMME_UPDATE"])

        self.role_assignment_user.role = role
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("PROGRAMME_CREATE", permissions)
        self.assertIn("PROGRAMME_UPDATE", permissions)

    def test_role_assignment_user_group_permissions(self) -> None:
        self.role_assignment_user.group = self.group
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn(self._get_permission_name_combined(self.permission), permissions)

    def test_role_assignment_partner_role_permissions(self) -> None:
        role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
        self.role_assignment_partner.role = role
        self.role_assignment_partner.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn("PROGRAMME_FINISH", permissions)

    def test_role_assignment_partner_group_permissions(self) -> None:
        self.role_assignment_partner.group = self.group
        self.role_assignment_partner.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)

        self.assertIn(self._get_permission_name_combined(self.permission), permissions)

    def test_has_perm_for_superuser(self) -> None:
        self.user.is_superuser = True
        self.user.save()

        self.assertTrue(self.backend.has_perm(self.user, f"{self.content_type.app_label}.{self.permission.codename}"))
        self.assertTrue(self.backend.has_perm(self.user, "PROGRAMME_FINISH", self.program))

    def test_role_expired(self) -> None:
        self.role_assignment_user.group = self.group
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)
        self.assertIn(self._get_permission_name_combined(self.permission), permissions)

        self.role_assignment_user.expiry_date = timezone.now() - timezone.timedelta(days=1)
        self.role_assignment_user.save()

        permissions = self.backend.get_all_permissions(self.user, self.business_area)
        self.assertNotIn(self._get_permission_name_combined(self.permission), permissions)

    def test_get_permissions_for_program(self) -> None:
        # User's Role Assignmenmts grants
        program_empty = ProgramFactory(
            status=Program.ACTIVE, name="Test Program Empty", business_area=self.business_area
        )
        role = RoleFactory(name="Role for Partner", permissions=["PROGRAMME_FINISH"])
        self.role_assignment_partner.role = role
        self.role_assignment_partner.program = self.program
        self.role_assignment_partner.save()

        self.role_assignment_user.program = program_empty
        self.role_assignment_user.save()

        role = RoleFactory(name="Role for User", permissions=["PROGRAMME_CREATE", "PROGRAMME_UPDATE"])
        self.role_assignment_user.role = role
        self.role_assignment_user.save()

        permissions_in_program = self.backend.get_all_permissions(self.user, self.program)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program)

        # no permissions for other program
        program_other = ProgramFactory(
            status=Program.ACTIVE, name="Test Program Other", business_area=self.business_area
        )
        permissions_in_program_other = self.backend.get_all_permissions(self.user, program_other)
        assert set() == permissions_in_program_other

        # permissions from user's RoleAssignment in program_empty
        permissions_in_program_empty = self.backend.get_all_permissions(self.user, program_empty)
        self.assertIn("PROGRAMME_CREATE", permissions_in_program_empty)
        self.assertIn("PROGRAMME_UPDATE", permissions_in_program_empty)
        self.assertNotIn("PROGRAMME_FINISH", permissions_in_program_other)

        # partner loses permission for the program and gets permission for the other
        self.role_assignment_partner.program = program_other
        self.role_assignment_partner.save()
        permissions_in_program = self.backend.get_all_permissions(self.user, self.program)
        assert set() == permissions_in_program
        permissions_in_program_other = self.backend.get_all_permissions(self.user, program_other)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program_other)
        self.assertNotIn("PROGRAMME_CREATE", permissions_in_program_other)
        self.assertNotIn("PROGRAMME_UPDATE", permissions_in_program_other)

        # user loses permission for the program and gets permission for the other
        self.role_assignment_user.program = program_other
        self.role_assignment_user.save()
        permissions_in_program_other = self.backend.get_all_permissions(self.user, program_other)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program_other)
        self.assertIn("PROGRAMME_CREATE", permissions_in_program_other)
        self.assertIn("PROGRAMME_UPDATE", permissions_in_program_other)

        # partner gets access to all programs in the business area (program=None)
        self.role_assignment_partner.program = None
        self.role_assignment_partner.save()
        permissions_in_program = self.backend.get_all_permissions(self.user, self.program)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program)
        self.assertNotIn("PROGRAMME_CREATE", permissions_in_program)
        self.assertNotIn("PROGRAMME_UPDATE", permissions_in_program)
        permissions_in_program_other = self.backend.get_all_permissions(self.user, program_other)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program_other)
        self.assertIn("PROGRAMME_CREATE", permissions_in_program_other)
        self.assertIn("PROGRAMME_UPDATE", permissions_in_program_other)

        # user gets access to all programs in the business area (program=None)
        self.role_assignment_user.program = None
        self.role_assignment_user.save()
        permissions_in_program = self.backend.get_all_permissions(self.user, self.program)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program)
        self.assertIn("PROGRAMME_CREATE", permissions_in_program)
        self.assertIn("PROGRAMME_UPDATE", permissions_in_program)
        permissions_in_program_other = self.backend.get_all_permissions(self.user, program_other)
        self.assertIn("PROGRAMME_FINISH", permissions_in_program_other)
        self.assertIn("PROGRAMME_CREATE", permissions_in_program_other)
        self.assertIn("PROGRAMME_UPDATE", permissions_in_program_other)

    def test_get_permissions_from_all_sources(self) -> None:
        program_for_user = ProgramFactory(
            status=Program.ACTIVE, name="Test Program For User", business_area=self.business_area
        )
        permission1 = Permission.objects.create(
            codename="test_permission1", name="Test Permission 1", content_type=self.content_type
        )
        permission2 = Permission.objects.create(
            codename="test_permission2", name="Test Permission 2", content_type=self.content_type
        )
        permission3 = Permission.objects.create(
            codename="test_permission3", name="Test Permission 3", content_type=self.content_type
        )
        # permission on a user group
        group_user = Group.objects.create(name="TestGroupUser")
        group_user.permissions.add(permission1)
        self.user.groups.add(group_user)

        # permission on a RoleAssignment group for user
        group_role_assignment_user = Group.objects.create(name="TestGroupRoleAssignmentUser")
        group_role_assignment_user.permissions.add(permission2)
        self.role_assignment_user.group = group_role_assignment_user
        self.role_assignment_user.program = program_for_user
        self.role_assignment_user.save()

        # permission on a RoleAssignment group for partner
        group_role_assignment_partner = Group.objects.create(name="TestGroupRoleAssignmentPartner")
        group_role_assignment_partner.permissions.add(permission3)
        self.role_assignment_partner.group = group_role_assignment_partner
        self.role_assignment_partner.program = self.program
        self.role_assignment_partner.save()

        # permission on a RoleAssignment role for user
        role_user = RoleFactory(name="Test Role User", permissions=["PROGRAMME_CREATE"])
        self.role_assignment_user.role = role_user
        self.role_assignment_user.save()

        # permission on a RoleAssignment role for partner
        role_partner = RoleFactory(name="Test Role Partner", permissions=["PROGRAMME_FINISH"])
        self.role_assignment_partner.role = role_partner
        self.role_assignment_partner.save()

        # outside-BA permissions (only from user's group)
        permissions = self.backend.get_all_permissions(self.user)
        assert {self._get_permission_name_combined(permission1)} == permissions

        # permissions for BA
        permissions = self.backend.get_all_permissions(self.user, self.business_area)
        self.assertIn(self._get_permission_name_combined(permission1), permissions)
        self.assertIn(self._get_permission_name_combined(permission2), permissions)
        self.assertIn(self._get_permission_name_combined(permission3), permissions)
        self.assertIn("PROGRAMME_CREATE", permissions)
        self.assertIn("PROGRAMME_FINISH", permissions)

        # permissions for other BA - empty
        business_area_other = create_ukraine()
        permissions = self.backend.get_all_permissions(self.user, business_area_other)
        assert set() == permissions

        # permissions for program
        # only RoleAssignment for partner is connected to this Program
        permissions = self.backend.get_all_permissions(self.user, self.program)
        self.assertIn(self._get_permission_name_combined(permission1), permissions)
        self.assertNotIn(self._get_permission_name_combined(permission2), permissions)
        self.assertIn(self._get_permission_name_combined(permission3), permissions)
        self.assertIn("PROGRAMME_FINISH", permissions)
        self.assertNotIn("PROGRAMME_CREATE", permissions)

        # permissions for program for user
        permissions = self.backend.get_all_permissions(self.user, program_for_user)
        self.assertIn(self._get_permission_name_combined(permission1), permissions)
        self.assertIn(self._get_permission_name_combined(permission2), permissions)
        self.assertNotIn(self._get_permission_name_combined(permission3), permissions)
        self.assertIn("PROGRAMME_CREATE", permissions)
        self.assertNotIn("PROGRAMME_FINISH", permissions)

        # permissions for other program - empty (neither partner nor user has access to this program)
        program_other = ProgramFactory(
            status=Program.ACTIVE, name="Test Program Other", business_area=self.business_area
        )
        permissions = self.backend.get_all_permissions(self.user, program_other)
        assert set() == permissions

    def _get_permission_name_combined(self, permission: Permission) -> str:
        return f"{self.content_type.app_label}.{permission.codename}"
