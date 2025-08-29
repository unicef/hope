from datetime import timedelta

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.caches import get_user_permissions_version_key
from hope.models.user import User
from hope.models.business_area import BusinessArea
from hope.models.program import Program


class TestSignalsForInvalidatePermissionCaches(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.business_area_afg = create_afghanistan()

        self.partner1 = PartnerFactory(name="Partner")
        self.partner2 = PartnerFactory(name="Partner 2")

        self.user1_partner1 = UserFactory(partner=self.partner1)
        self.user2_partner1 = UserFactory(partner=self.partner1)
        self.user1_partner2 = UserFactory(partner=self.partner2)
        self.user2_partner2 = UserFactory(partner=self.partner2)

        self.role1 = RoleFactory(name="Role 1")
        self.role2 = RoleFactory(name="Role 2")

        self.program = ProgramFactory.create(
            status=Program.DRAFT,
            business_area=self.business_area_afg,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )

        self.role_assignment1 = RoleAssignmentFactory(
            user=self.user1_partner1,
            partner=None,
            role=self.role1,
            business_area=self.business_area_afg,
        )
        self.role_assignment2 = RoleAssignmentFactory(
            user=self.user1_partner2,
            partner=None,
            role=self.role1,
            business_area=self.business_area_afg,
        )
        self.role_assignment3 = RoleAssignmentFactory(
            user=None,
            partner=self.partner1,
            role=self.role2,
            business_area=self.business_area_afg,
        )

        # group on a user
        self.group1 = Group.objects.create(name="Test Group")
        self.content_type = ContentType.objects.get_for_model(BusinessArea)
        permission = Permission.objects.create(
            codename="test_permission",
            name="Test Permission",
            content_type=self.content_type,
        )
        self.group1.permissions.add(permission)
        self.user1_partner1.groups.add(self.group1)

        # group on a user's role assignment
        self.group2 = Group.objects.create(name="Test Group 2")
        self.role_assignment2.group = self.group2
        self.role_assignment2.save()

        # group on a partner's role assignment
        self.group3 = Group.objects.create(name="Test Group 3")
        self.role_assignment3.group = self.group3
        self.role_assignment3.save()

        self.version_key_user1_partner1_before = self._get_cache_version(self.user1_partner1)
        self.version_key_user2_partner1_before = self._get_cache_version(self.user2_partner1)
        self.version_key_user1_partner2_before = self._get_cache_version(self.user1_partner2)
        self.version_key_user2_partner2_before = self._get_cache_version(self.user2_partner2)

    def test_invalidate_cache_on_user_change(self) -> None:
        self.user1_partner1.is_superuser = True
        self.user1_partner1.save()
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1

        self.user1_partner1.partner = self.partner2
        self.user1_partner1.save()

        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 2

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_role_change_for_user(self) -> None:
        self.role1.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
        self.role1.save()

        # users with role_assignments connected to the role should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_role_change_for_partner(self) -> None:
        self.role2.permissions = ["PROGRAMME_CREATE", "PROGRAMME_FINISH"]
        self.role2.save()

        # users with partner's role_assignments connected to the role should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_permissions_change_for_user(self) -> None:
        permission = Permission.objects.create(
            codename="test_permission_new_1",
            name="Test Permission 2",
            content_type=self.content_type,
        )
        self.group1.permissions.add(permission)

        # users connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

        # remove permission from the group
        self.group1.permissions.remove(permission)

        # users connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 2

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_permissions_change_for_user_role_assignment(
        self,
    ) -> None:
        permission = Permission.objects.create(
            codename="test_permission_new_2",
            name="Test Permission 2",
            content_type=self.content_type,
        )
        self.group2.permissions.add(permission)

        # users with role_assignments connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

        # remove permission from the group
        self.group2.permissions.remove(permission)

        # users with role_assignments connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before + 2

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_permissions_change_for_partner_role_assignment(
        self,
    ) -> None:
        permission = Permission.objects.create(
            codename="test_permission_new_3",
            name="Test Permission 2",
            content_type=self.content_type,
        )
        self.group3.permissions.add(permission)

        # users with partner with role_assignments connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

        # remove permission from the group
        self.group3.permissions.remove(permission)

        # users with partner with role_assignments connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 2
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before + 2
        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_change_for_user(self) -> None:
        self.user1_partner1.groups.remove(self.group1)

        # user with changed group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_delete_for_user(self) -> None:
        self.group1.delete()

        # users connected with the group should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 1

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_delete_for_user_role_assignment(self) -> None:
        self.group2.delete()
        # users with role_assignments connected with the group should have their cache invalidated
        # increased by additional 2 signals:
        # * signal on the  RoleAssignment
        # * signal on User update triggered because of cascade delete of the RoleAssignment
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before + 3

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_group_delete_for_partner_role_assignment(self) -> None:
        self.group3.delete()

        # users with partner with role_assignments connected with the group should have their cache invalidated
        # increased by 2 because of the signal on the  RoleAssignment as well
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 2
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before + 2

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_role_assignment_change_for_user(self) -> None:
        self.role_assignment1.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment1.save()

        self.role_assignment1.group = self.group3
        self.role_assignment1.save()

        self.role_assignment1.role = self.role2
        self.role_assignment1.save()

        # users connected to the role_assignment should have their cache invalidated
        # +6: 3 signals on RoleAssignment and 3 signals on User to update modify_date because of role_assignment change
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 6

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    def test_invalidate_cache_on_role_assignment_change_for_partner(self) -> None:
        self.role_assignment3.expiry_date = (timezone.now() - timedelta(days=1)).date()
        self.role_assignment3.save()

        self.role_assignment3.program = self.program
        self.role_assignment3.save()

        self.role_assignment3.role = self.role1
        self.role_assignment3.save()

        # users with partner connected to the role_assignment should have their cache invalidated
        assert self._get_cache_version(self.user1_partner1) == self.version_key_user1_partner1_before + 3
        assert self._get_cache_version(self.user2_partner1) == self.version_key_user2_partner1_before + 3

        # no invalidation for the rest of the users
        assert self._get_cache_version(self.user1_partner2) == self.version_key_user1_partner2_before
        assert self._get_cache_version(self.user2_partner2) == self.version_key_user2_partner2_before

    @staticmethod
    def _get_cache_version(user: User) -> int:
        version_key = get_user_permissions_version_key(user)
        return cache.get(version_key)

    def tearDown(self) -> None:
        super().tearDown()
        cache.clear()
