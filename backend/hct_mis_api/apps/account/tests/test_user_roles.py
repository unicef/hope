from django.forms.models import inlineformset_factory
from django.test import TestCase

from hct_mis_api.apps.account.admin import UserRoleAdminForm, UserRoleInlineFormSet
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User, UserRole
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea


class UserRolesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role_1 = Role.objects.create(name="Role_1")
        cls.role_2 = Role.objects.create(name="Role_2")
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory()

    def test_user_can_be_assigned_role(self):
        data = {"role": self.role_1.id, "user": self.user.id, "business_area": self.business_area.id}
        form = UserRoleAdminForm(data=data)
        self.assertTrue(form.is_valid())

    def test_user_cannot_be_assigned_incompatible_role_in_same_business_area(self):
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)
        userrole = UserRole.objects.create(role=self.role_1, business_area=self.business_area, user=self.user)

        data = {"role": self.role_2.id, "user": self.user.id, "business_area": self.business_area.id}
        form = UserRoleAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors.keys())
        self.assertIn(f"This role is incompatible with {self.role_1.name}", form.errors["role"])

        # reverse role from incompatible roles pair
        userrole.role = self.role_2
        userrole.save()
        data["role"] = self.role_1.id
        form = UserRoleAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors.keys())
        self.assertIn(f"This role is incompatible with {self.role_2.name}", form.errors["role"])

    def test_assign_multiple_roles_for_user_at_the_same_time(self):
        data = {
            "user_roles-TOTAL_FORMS": "2",
            "user_roles-INITIAL_FORMS": "0",
            "user_roles-0-role": self.role_1.id,
            "user_roles-1-role": self.role_2.id,
            "user_roles-0-business_area": self.business_area.id,
            "user_roles-1-business_area": self.business_area.id,
        }
        UserRoleFormSet = inlineformset_factory(User, UserRole, fields=("__all__"), formset=UserRoleInlineFormSet)
        formset = UserRoleFormSet(instance=self.user, data=data)
        self.assertTrue(formset.is_valid())

    def test_assign_multiple_roles_for_user_at_the_same_time_fails_for_incompatible_roles(self):
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)

        data = {
            "user_roles-TOTAL_FORMS": "2",
            "user_roles-INITIAL_FORMS": "0",
            "user_roles-0-role": self.role_1.id,
            "user_roles-1-role": self.role_2.id,
            "user_roles-0-business_area": self.business_area.id,
            "user_roles-1-business_area": self.business_area.id,
        }
        UserRoleFormSet = inlineformset_factory(User, UserRole, fields=("__all__"), formset=UserRoleInlineFormSet)
        formset = UserRoleFormSet(instance=self.user, data=data)
        self.assertFalse(formset.is_valid())
        self.assertEqual(len(formset.errors), 2)
        self.assertIn(f"{self.role_1.name} is incompatible with {self.role_2.name}.", formset.errors[0]["role"])
