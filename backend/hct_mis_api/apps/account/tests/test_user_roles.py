from django.test import TestCase
from django.core.management import call_command

from account.models import IncompatibleRoles, Role, UserRole
from account.admin import UserRoleAdminForm
from core.models import BusinessArea
from account.fixtures import UserFactory


class UserRolesTest(TestCase):
    def setUp(self):
        self.role_1 = Role.objects.create(name="Role_1")
        self.role_2 = Role.objects.create(name="Role_2")
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user = UserFactory()

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

    # def test_assign_multiple_roles_for_user_at_the_same_time(self):
    #     data = {
    #         "form-TOTAL_FORMS": "2",
    #         "form-INITIAL_FORMS": "0",
    #         "form-0-role": self.role_1.id,
    #         "form-1-role": self.role_2.id,
    #         # "form-0-user": self.user.id,
    #         # "form-1-user": self.user.id,
    #         "form-0-business_area": self.business_area.id,
    #         "form-1-business_area": self.business_area.id,
    #     }
    #     formset = UserRoleInlineFormSet(data, instance=self.user)
    #     formset.is_valid()
    #     print(formset)
    #     print(formset.errors)
