from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, UserRole
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan


class IncompatibleRolesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role_1 = Role.objects.create(name="Role_1")
        cls.role_2 = Role.objects.create(name="Role_2")

    def test_unique_pair_allowed(self):
        test_role = IncompatibleRoles(role_one=self.role_1, role_two=self.role_2)
        test_role.full_clean()
        test_role.save()
        self.assertTrue(IncompatibleRoles.objects.filter(role_one=self.role_1, role_two=self.role_2).exists())

    def test_roles_must_be_different(self):
        incomp_role = IncompatibleRoles(role_one=self.role_1, role_two=self.role_1)
        with self.assertRaisesMessage(ValidationError, "Choose two different roles."):
            incomp_role.full_clean()

    def test_only_unique_combinations_allowed(self):
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)

        test_role = IncompatibleRoles(role_one=self.role_2, role_two=self.role_1)
        with self.assertRaisesMessage(
            ValidationError, "This combination of roles already exists as incompatible pair."
        ):
            test_role.full_clean()

    def test_any_users_already_with_both_roles(self):
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        user = UserFactory()
        UserRole.objects.create(role=self.role_1, business_area=business_area, user=user)
        UserRole.objects.create(role=self.role_2, business_area=business_area, user=user)

        test_role = IncompatibleRoles(role_one=self.role_1, role_two=self.role_2)

        with self.assertRaisesMessage(
            ValidationError,
            f"Users: [{user.email}] have these roles assigned to them in the same business area. Please fix them before creating this incompatible roles pair.",
        ):
            test_role.full_clean()
