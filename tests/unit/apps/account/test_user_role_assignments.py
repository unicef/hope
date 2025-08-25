from typing import TYPE_CHECKING, List

from django.forms.models import inlineformset_factory
from django.test import TestCase
from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine

from hope.admin.account_forms import (
    RoleAssignmentAdminForm,
    RoleAssignmentInlineFormSet,
)
from hope.models.user import User
from hope.models.role_assignment import RoleAssignment
from hope.models.incompatible_roles import IncompatibleRoles
from hope.models.role import Role
from hope.apps.account.permissions import (
    DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER,
    Permissions,
)
from hope.models.core import BusinessArea

if TYPE_CHECKING:
    from django.forms.utils import ErrorList


class RoleAssignmentsTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.role_1 = Role.objects.create(name="Role_1")
        cls.role_2 = Role.objects.create(name="Role_2")
        create_afghanistan()
        create_ukraine()
        cls.business_area_afg = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area_ukr = BusinessArea.objects.get(slug="ukraine")
        cls.user = UserFactory()

    def test_user_can_be_assigned_role(self) -> None:
        data = {
            "role": self.role_1.id,
            "user": self.user.id,
            "business_area": self.business_area_afg.id,
        }
        form = RoleAssignmentAdminForm(data=data)
        assert form.is_valid()

    def test_user_cannot_be_assigned_incompatible_role_in_same_business_area(
        self,
    ) -> None:
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)
        user_role = RoleAssignment.objects.create(
            role=self.role_1, business_area=self.business_area_afg, user=self.user
        )

        data = {
            "role": self.role_2.id,
            "user": self.user.id,
            "business_area": self.business_area_afg.id,
        }
        form = RoleAssignmentAdminForm(data=data)
        assert not form.is_valid()
        assert "role" in form.errors
        assert f"This role is incompatible with {self.role_1.name}" in form.errors["role"]

        # reverse role from incompatible roles pair
        user_role.role = self.role_2
        user_role.save()
        data["role"] = self.role_1.id
        form = RoleAssignmentAdminForm(data=data)
        assert not form.is_valid()
        assert "role" in form.errors
        assert f"This role is incompatible with {self.role_2.name}" in form.errors["role"]

    def test_assign_multiple_roles_for_user_at_the_same_time(self) -> None:
        data = {
            "role_assignments-TOTAL_FORMS": "2",
            "role_assignments-INITIAL_FORMS": "0",
            "role_assignments-0-role": self.role_1.id,
            "role_assignments-1-role": self.role_2.id,
            "role_assignments-0-business_area": self.business_area_afg.id,
            "role_assignments-1-business_area": self.business_area_afg.id,
        }
        RoleAssignmentFormSet = inlineformset_factory(  # noqa
            User,
            RoleAssignment,
            fields=("__all__"),
            formset=RoleAssignmentInlineFormSet,
        )
        formset = RoleAssignmentFormSet(instance=self.user, data=data)
        assert formset.is_valid()

    def test_assign_multiple_roles_for_user_at_the_same_time_fails_for_incompatible_roles(
        self,
    ) -> None:
        IncompatibleRoles.objects.create(role_one=self.role_1, role_two=self.role_2)

        data = {
            "role_assignments-TOTAL_FORMS": "2",
            "role_assignments-INITIAL_FORMS": "0",
            "role_assignments-0-role": self.role_1.id,
            "role_assignments-1-role": self.role_2.id,
            "role_assignments-0-business_area": self.business_area_afg.id,
            "role_assignments-1-business_area": self.business_area_afg.id,
        }
        RoleAssignmentFormSet = inlineformset_factory(  # noqa
            User,
            RoleAssignment,
            fields=("__all__"),
            formset=RoleAssignmentInlineFormSet,
        )
        formset = RoleAssignmentFormSet(instance=self.user, data=data)
        assert not formset.is_valid()
        assert len(formset.errors) == 2

        errors: List[ErrorList] = formset.errors
        role = errors[0]["role"]  # type: ignore # mypy doesn't see that you can call __getitem__ with str on ErrorList
        assert f"{self.role_1.name} is incompatible with {self.role_2.name}." in role

    def test_user_role_exclude_by_expiry_date(self) -> None:
        user_not_unicef_partner = UserFactory(partner=PartnerFactory(name="Test123"))
        role_1 = Role.objects.create(name="111", permissions=[Permissions.RDI_VIEW_LIST.value])
        role_2 = Role.objects.create(name="222", permissions=[Permissions.PM_EXPORT_PDF_SUMMARY.value])
        # user_role_active
        user_role_1 = RoleAssignment.objects.create(
            role=role_1,
            business_area=self.business_area_afg,
            user=user_not_unicef_partner,
        )
        # user_role_inactive
        user_role_2 = RoleAssignment.objects.create(
            role=role_2,
            business_area=self.business_area_afg,
            user=user_not_unicef_partner,
            expiry_date="2024-02-16",
        )
        # user_role_active_but_sharing_same_role_with_user_role_inactive
        RoleAssignment.objects.create(
            role=role_2,
            business_area=self.business_area_ukr,
            user=user_not_unicef_partner,
        )

        assert Permissions.RDI_VIEW_LIST.value in user_not_unicef_partner.permissions_in_business_area(
            self.business_area_afg.slug
        )
        assert Permissions.PM_EXPORT_PDF_SUMMARY.value not in user_not_unicef_partner.permissions_in_business_area(
            self.business_area_afg.slug
        )
        assert Permissions.PM_EXPORT_PDF_SUMMARY.value in user_not_unicef_partner.permissions_in_business_area(
            self.business_area_ukr.slug
        )

        user_role_1.expiry_date = "2024-02-02"
        user_role_1.save()
        user_role_1.refresh_from_db()
        assert str(user_role_1.expiry_date) == "2024-02-02"
        assert str(user_role_2.expiry_date) == "2024-02-16"
        # empty list
        assert user_not_unicef_partner.permissions_in_business_area(self.business_area_afg.slug) == set()
        assert Permissions.RDI_VIEW_LIST.value not in user_not_unicef_partner.permissions_in_business_area(
            self.business_area_afg.slug
        )
        assert Permissions.PM_EXPORT_PDF_SUMMARY.value not in user_not_unicef_partner.permissions_in_business_area(
            self.business_area_afg.slug
        )

    def test_unicef_partner_hq_has_permission_from_user_and_role_with_all_permissions(
        self,
    ) -> None:
        partner = PartnerFactory(name="UNICEF")
        unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner)
        user = UserFactory(partner=unicef_hq)
        role = Role.objects.create(name="111", permissions=[Permissions.GRIEVANCES_CREATE.value])
        RoleAssignment.objects.create(role=role, business_area=self.business_area_afg, user=user)

        assert Permissions.GRIEVANCES_CREATE.value in user.permissions_in_business_area(self.business_area_afg.slug)

        # assert role with all permissions
        role_with_all_permissions = RoleFactory(name="Role with all permissions")
        permissions = [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        ]
        role_with_all_permissions.permissions = [permission.value for permission in permissions]
        role_with_all_permissions.save()

        for permission in permissions:
            assert permission.value in user.permissions_in_business_area(self.business_area_afg.slug)

        assert Permissions.GRIEVANCES_UPDATE.value not in user.permissions_in_business_area(self.business_area_afg.slug)

    def test_unicef_partner_per_ba_has_permission_from_user_and_role_with_default_permissions(
        self,
    ) -> None:
        partner = PartnerFactory(name="UNICEF")
        unicef_in_afg = PartnerFactory(name=f"UNICEF Partner for {self.business_area_afg.slug}", parent=partner)
        user = UserFactory(partner=unicef_in_afg)
        role = Role.objects.create(name="111", permissions=[Permissions.GRIEVANCES_CREATE.value])
        RoleAssignment.objects.create(role=role, business_area=self.business_area_afg, user=user)

        assert Permissions.GRIEVANCES_CREATE.value in user.permissions_in_business_area(self.business_area_afg.slug)

        for permission in DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER:
            assert permission.value in user.permissions_in_business_area(self.business_area_afg.slug)

        assert Permissions.GRIEVANCES_UPDATE.value not in user.permissions_in_business_area(self.business_area_afg.slug)
