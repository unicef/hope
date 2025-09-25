from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django.utils import timezone

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from hope.apps.account.permissions import Permissions
from hope.models.business_area import BusinessArea
from hope.models.program import Program
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment


class AllPermissionsInBusinessAreasTest(TransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        # Create business areas and ensure they're active
        create_afghanistan()
        create_ukraine()
        self.business_area_afg = BusinessArea.objects.get(slug="afghanistan")
        self.business_area_ukr = BusinessArea.objects.get(slug="ukraine")

        # Ensure business areas are active (required for all_permissions_in_business_areas)
        self.business_area_afg.active = True
        self.business_area_afg.save()
        self.business_area_ukr.active = True
        self.business_area_ukr.save()

        # Create roles with different permissions
        self.role_rdi = Role.objects.create(
            name="RDI Role Test", permissions=[Permissions.RDI_VIEW_LIST.value, Permissions.RDI_VIEW_DETAILS.value]
        )
        self.role_program = Role.objects.create(
            name="Program Role Test",
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value, Permissions.PROGRAMME_CREATE.value],
        )

        # Create partner and user
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)

    def clear_user_cache(self, user):
        """Clear cached properties for the user."""
        if hasattr(user, "_all_permissions_in_business_areas"):
            delattr(user, "_all_permissions_in_business_areas")
        if hasattr(user, "_program_ids_for_business_area_cache"):
            delattr(user, "_program_ids_for_business_area_cache")

    def test_basic_functionality(self) -> None:
        """Test basic functionality with roles in different business areas."""
        # Create role assignments for user in different business areas
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )
        RoleAssignment.objects.create(
            role=self.role_program,
            business_area=self.business_area_ukr,
            user=self.user,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas

        # Check Afghanistan permissions
        afg_permissions = permissions[str(self.business_area_afg.id)]
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value not in afg_permissions

        # Check Ukraine permissions
        ukr_permissions = permissions[str(self.business_area_ukr.id)]
        assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in ukr_permissions
        assert Permissions.PROGRAMME_CREATE.value in ukr_permissions
        assert Permissions.RDI_VIEW_LIST.value not in ukr_permissions

    def test_multiple_roles_same_business_area(self) -> None:
        """Test multiple role assignments in the same business area."""
        # Create multiple role assignments in same business area
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )
        RoleAssignment.objects.create(
            role=self.role_program,
            business_area=self.business_area_afg,
            user=self.user,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should have permissions from both roles
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_CREATE.value in afg_permissions

    def test_excludes_expired_roles(self) -> None:
        """Test that expired role assignments are excluded."""
        # Create active role assignment
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )

        # Create expired role assignment
        expired_date = timezone.now().date() - timezone.timedelta(days=1)
        RoleAssignment.objects.create(
            role=self.role_program,
            business_area=self.business_area_afg,
            user=self.user,
            expiry_date=expired_date,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should only have permissions from active role
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value not in afg_permissions
        assert Permissions.PROGRAMME_CREATE.value not in afg_permissions

    def test_includes_future_expiry_roles(self) -> None:
        """Test that role assignments with future expiry dates are included."""
        # Create role assignment with future expiry date
        future_date = timezone.now().date() + timezone.timedelta(days=30)
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
            expiry_date=future_date,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should have permissions from role with future expiry
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions

    def test_includes_no_expiry_roles(self) -> None:
        """Test that role assignments with no expiry date are included."""
        # Create role assignment with no expiry
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
            expiry_date=None,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should have permissions from role with no expiry
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions

    def test_empty_for_no_roles(self) -> None:
        """Test that method returns empty dict when user has no role assignments."""
        # User with no role assignments
        partner = PartnerFactory(name="Test Partner Empty")
        user = UserFactory(partner=partner)

        permissions = user.all_permissions_in_business_areas

        # Should be empty dict
        assert permissions == {}

    def test_with_partner_roles(self) -> None:
        """Test permissions from partner role assignments."""
        # Add business area to partner's allowed business areas
        self.partner.allowed_business_areas.add(self.business_area_afg)

        # User role assignment
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )

        # Partner role assignment
        RoleAssignment.objects.create(
            role=self.role_program,
            business_area=self.business_area_afg,
            partner=self.partner,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should have permissions from both user and partner roles
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value in afg_permissions
        assert Permissions.PROGRAMME_CREATE.value in afg_permissions

    def test_with_django_groups(self) -> None:
        """Test permissions from Django groups in role assignments."""
        # Create Django group with permissions
        content_type = ContentType.objects.get_for_model(Program)

        # Try to get existing permission first
        try:
            program_permission = Permission.objects.get(
                codename="view_program",
                content_type=content_type,
            )
        except Permission.DoesNotExist:
            program_permission = Permission.objects.create(
                codename="view_program",
                name="Can view program",
                content_type=content_type,
            )

        # Create unique group name with timestamp to avoid conflicts
        import time

        group_name = f"Program Viewers Test {int(time.time())}"
        django_group = Group.objects.create(name=group_name)
        django_group.permissions.add(program_permission)

        # Role assignment with Django group
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
            group=django_group,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas
        afg_permissions = permissions[str(self.business_area_afg.id)]

        # Should have role permissions
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions
        assert Permissions.RDI_VIEW_DETAILS.value in afg_permissions

        # Should have Django group permissions
        assert "program.view_program" in afg_permissions

    def test_return_types(self) -> None:
        """Test that the method returns the correct data types."""
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )

        permissions = self.user.all_permissions_in_business_areas

        # Should return dict
        assert isinstance(permissions, dict)

        # Keys should be strings (business area IDs)
        for key in permissions:
            assert isinstance(key, str)

        # Values should be sets of strings (permissions)
        for value in permissions.values():
            assert isinstance(value, set)
            for permission in value:
                assert isinstance(permission, str)

    def test_caching_behavior(self) -> None:
        """Test that the method uses caching properly."""
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
        )

        # First call should execute query
        permissions1 = self.user.all_permissions_in_business_areas

        # Second call should use cached result
        permissions2 = self.user.all_permissions_in_business_areas

        # Should be the same object (cached)
        assert permissions1 is permissions2

        # Should have correct permissions
        afg_permissions = permissions1[str(self.business_area_afg.id)]
        assert Permissions.RDI_VIEW_LIST.value in afg_permissions

    @patch("hope.apps.account.models.timezone.now")
    def test_expiry_date_edge_case(self, mock_now) -> None:
        """Test expiry date filtering on exact boundary."""
        # Set current time - beginning of next day so that today's date is < timezone.now()
        current_time = timezone.datetime(2024, 1, 16, 0, 0, 1, tzinfo=timezone.utc)
        mock_now.return_value = current_time

        # Role assignment expiring yesterday (should be excluded)
        yesterday = timezone.datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc).date()
        RoleAssignment.objects.create(
            role=self.role_rdi,
            business_area=self.business_area_afg,
            user=self.user,
            expiry_date=yesterday,
        )

        self.clear_user_cache(self.user)
        permissions = self.user.all_permissions_in_business_areas

        # Role expiring yesterday should NOT be included (expiry_date < timezone.now())
        assert len(permissions) == 0
