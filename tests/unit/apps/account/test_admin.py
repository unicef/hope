import json
from typing import Any, Optional, Union
from unittest.mock import MagicMock
from urllib.parse import unquote

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django_webtest import DjangoTestApp
import pytest

from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from hope.admin.account_forms import RoleAssignmentAdminForm
from hope.admin.partner import PartnerAdmin
from hope.admin.user_role import PartnerRoleAssignmentAdmin, RoleAssignmentInline, UserRoleAssignmentAdmin
from hope.models import IncompatibleRoles, Partner, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db()


@pytest.fixture
def superuser(request: pytest.FixtureRequest, partner_unicef: Partner) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def role(request: pytest.FixtureRequest) -> Role:
    return RoleFactory(name="Role")


def test_role_perm_matrix(django_app: DjangoTestApp, superuser: pytest.FixtureRequest) -> None:
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


@pytest.mark.xfail
def test_role_sync(django_app: DjangoTestApp, superuser: User, role: Role) -> None:
    url = reverse("admin:account_role_dumpdata_qs")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200
    jres = json.loads(unquote(res.json["data"]))
    models = {item["model"] for item in jres}
    assert len(models) == 1
    assert models == {"account.role"}


class RoleAssignmentInlineTest(TestCase):
    def setUp(self) -> None:
        self.request = RequestFactory()
        self.site = AdminSite()
        self.admin = RoleAssignmentInline(parent_model=Partner, admin_site=self.site)

        self.user = UserFactory()
        self.unicef_parent = PartnerFactory(name="UNICEF")
        self.unicef_subpartner = PartnerFactory(parent=self.unicef_parent)
        self.partner_without_parent = PartnerFactory(parent=None, name="Parent without parent")
        self.business_area = create_afghanistan()
        self.other_ba = BusinessAreaFactory(name="Ukraine")
        self.unicef_subpartner.allowed_business_areas.set([self.business_area])
        self.role = RoleFactory(is_available_for_partner=True)
        self.role_not_available = RoleFactory(is_available_for_partner=False)

    def get_mock_request(self, object_id: Any = None) -> Union[WSGIRequest, WSGIRequest]:
        request = self.request.get("/")
        request.resolver_match = MagicMock()
        request.resolver_match.kwargs = {"object_id": str(object_id) if object_id else None}
        request.user = MagicMock()
        request.user.can_add_business_area_to_partner = MagicMock(return_value=True)
        return request

    def test_formfield_for_foreignkey_business_area(self) -> None:
        request = self.get_mock_request(object_id=self.unicef_subpartner.id)

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
        assert self.business_area in field.queryset
        assert self.other_ba not in field.queryset

        request = self.get_mock_request(object_id="some not digit string")

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
        assert self.business_area in field.queryset
        assert self.other_ba in field.queryset

    def test_formfield_for_foreignkey_role(self) -> None:
        request = self.get_mock_request(object_id=self.unicef_subpartner.id)

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
        assert self.role in field.queryset
        assert self.role_not_available not in field.queryset

        request = self.get_mock_request(object_id="some not digit string")

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
        assert self.role in field.queryset
        assert self.role_not_available in field.queryset

    def test_has_add_permission(self) -> None:
        request = self.get_mock_request(object_id=self.unicef_subpartner.id)
        assert self.admin.has_add_permission(request, self.unicef_subpartner)

        assert self.admin.has_add_permission(request, self.partner_without_parent)

        assert self.admin.has_add_permission(request, self.user)

    def test_has_change_permission(self) -> None:
        request = self.get_mock_request(object_id=self.unicef_subpartner.id)
        assert self.admin.has_change_permission(request, self.unicef_subpartner)

        assert self.admin.has_change_permission(request, self.unicef_parent)

        assert self.admin.has_change_permission(request, self.partner_without_parent)

        assert self.admin.has_change_permission(request, self.user)

    def test_has_delete_permission(self) -> None:
        request = self.get_mock_request(object_id=self.unicef_subpartner.id)
        assert self.admin.has_delete_permission(request, self.unicef_subpartner)

        assert self.admin.has_delete_permission(request, self.unicef_parent)

        assert self.admin.has_delete_permission(request, self.partner_without_parent)

        assert self.admin.has_delete_permission(request, self.user)


class UserRoleAssignmentAdminTest(TestCase):
    def setUp(self) -> None:
        self.request = RequestFactory()
        self.site = AdminSite()
        self.admin = UserRoleAssignmentAdmin(model=RoleAssignment, admin_site=self.site)

        self.user = UserFactory(username="testuser", is_staff=True)
        self.business_area = create_afghanistan()
        self.role = RoleFactory()
        self.role_assignment = RoleAssignmentFactory(
            user=self.user,
            role=self.role,
            business_area=self.business_area,
        )

    def get_mock_request(self, user: Optional[User] = None) -> Union[WSGIRequest, WSGIRequest]:
        """Helper to create a mock request"""
        request = self.request.get("/")
        request.user = user if user else self.user
        return request

    def test_get_queryset(self) -> None:
        request = self.get_mock_request()
        queryset = self.admin.get_queryset(request)
        assert self.role_assignment in queryset

    def test_get_actions(self) -> None:
        request = self.get_mock_request()
        actions = self.admin.get_actions(request)
        assert isinstance(actions, dict)

    def test_check_sync_permission(self) -> None:
        request = self.get_mock_request()
        assert self.admin.check_sync_permission(request)

        request.user.is_staff = False
        request.user.save()
        assert not self.admin.check_sync_permission(request)

    def test_check_publish_permission(self) -> None:
        request = self.get_mock_request()
        assert not self.admin.check_publish_permission(request)

    def test_get_queryset_filters_user_only(self) -> None:
        partner = PartnerFactory()
        partner.allowed_business_areas.add(self.business_area)
        partner_role_assignment = RoleAssignmentFactory(
            partner=partner,
            role=self.role,
            business_area=self.business_area,
        )

        request = self.get_mock_request()
        queryset = self.admin.get_queryset(request)

        # Should only include user role assignments
        assert self.role_assignment in queryset
        assert partner_role_assignment not in queryset

    def test_get_fields(self) -> None:
        request = self.get_mock_request()
        fields = self.admin.get_fields(request)

        assert "user" in fields
        assert "partner" not in fields
        assert "business_area" in fields
        assert "program" in fields
        assert "role" in fields
        assert "expiry_date" in fields
        assert "group" in fields

    def test_has_permissions_require_can_edit_user_roles(self) -> None:
        user_with_perm = UserFactory(username="user_with_perm", is_staff=True)
        for permission in [
            "view_roleassignment",
            "add_roleassignment",
            "change_roleassignment",
            "delete_roleassignment",
        ]:
            user_with_perm.user_permissions.add(Permission.objects.get(codename=permission))

        user_without_perm = UserFactory(username="user_without_perm", is_staff=True)

        request_with_perm = self.get_mock_request(user=user_with_perm)
        request_without_perm = self.get_mock_request(user=user_without_perm)

        # With permission
        assert self.admin.has_module_permission(request_with_perm)
        assert self.admin.has_view_permission(request_with_perm)
        assert self.admin.has_add_permission(request_with_perm)
        assert self.admin.has_change_permission(request_with_perm)
        assert self.admin.has_delete_permission(request_with_perm)

        # Without permission
        assert not self.admin.has_module_permission(request_without_perm)
        assert not self.admin.has_view_permission(request_without_perm)
        assert not self.admin.has_add_permission(request_without_perm)
        assert not self.admin.has_change_permission(request_without_perm)
        assert not self.admin.has_delete_permission(request_without_perm)


class PartnerRoleAssignmentAdminTest(TestCase):
    def setUp(self) -> None:
        self.request = RequestFactory()
        self.site = AdminSite()
        self.admin = PartnerRoleAssignmentAdmin(model=RoleAssignment, admin_site=self.site)

        self.partner = PartnerFactory()
        self.business_area = create_afghanistan()
        self.partner.allowed_business_areas.add(self.business_area)

        self.role_available = RoleFactory(name="Role Available", is_available_for_partner=True)
        self.role_not_available = RoleFactory(name="Role Not Available", is_available_for_partner=False)

        self.partner_role_assignment = RoleAssignmentFactory(
            partner=self.partner,
            role=self.role_available,
            business_area=self.business_area,
        )

    def get_mock_request(self, user: Optional[User] = None) -> Union[WSGIRequest, WSGIRequest]:
        """Helper to create a mock request"""
        request = self.request.get("/")
        request.user = user if user else UserFactory(is_staff=True)
        return request

    def test_get_queryset_filters_partner_only(self) -> None:
        user = UserFactory()
        user_role_assignment = RoleAssignmentFactory(
            user=user,
            role=self.role_available,
            business_area=self.business_area,
        )

        request = self.get_mock_request()
        queryset = self.admin.get_queryset(request)

        # Should only include partner role assignments
        assert self.partner_role_assignment in queryset
        assert user_role_assignment not in queryset

    def test_get_fields(self) -> None:
        request = self.get_mock_request()
        fields = self.admin.get_fields(request)

        assert "partner" in fields
        assert "user" not in fields
        assert "business_area" in fields
        assert "program" in fields
        assert "role" in fields
        assert "expiry_date" in fields
        assert "group" in fields

    def test_formfield_for_foreignkey_role_filters_partner_available(self) -> None:
        request = self.get_mock_request()

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)

        # Should only show roles available for partners
        assert self.role_available in field.queryset
        assert self.role_not_available not in field.queryset

    def test_formfield_for_foreignkey_business_area_filters_split(self) -> None:
        business_area_split = BusinessAreaFactory(name="Split BA", is_split=True)

        request = self.get_mock_request()

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)

        # Should exclude split business areas
        assert self.business_area in field.queryset
        assert business_area_split not in field.queryset


class RoleAssignmentAdminFormTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.form_class = RoleAssignmentAdminForm
        cls.business_area = create_afghanistan()
        cls.role_1 = RoleFactory(name="Role 1")
        cls.role_2 = RoleFactory(name="Role 2")
        cls.role_3 = RoleFactory(name="Role 3")

        IncompatibleRoles.objects.create(role_one=cls.role_1, role_two=cls.role_2)

    def test_user_incompatible_roles_create(self) -> None:
        user = UserFactory()

        # User already has role_1
        RoleAssignmentFactory(user=user, role=self.role_1, business_area=self.business_area)

        # Try to assign incompatible role_2
        form = self.form_class(
            data={
                "user": user.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            }
        )

        assert not form.is_valid()
        assert "role" in form.errors
        assert f"This role is incompatible with {self.role_1.name}" in form.errors["role"]

    def test_user_incompatible_roles_edit_exclude_self(self) -> None:
        user = UserFactory()

        role_assignment = RoleAssignmentFactory(user=user, role=self.role_1, business_area=self.business_area)

        # Edit the same assignment
        form = self.form_class(
            data={
                "user": user.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            },
            instance=role_assignment,
        )

        # Should be valid because we exclude the current instance
        assert form.is_valid()

    def test_partner_incompatible_roles_create(self) -> None:
        partner = PartnerFactory()
        partner.allowed_business_areas.add(self.business_area)

        RoleAssignmentFactory(partner=partner, role=self.role_1, business_area=self.business_area)

        # Try to assign incompatible role_2
        form = self.form_class(
            data={
                "partner": partner.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            }
        )

        assert not form.is_valid()
        assert "role" in form.errors
        assert f"This role is incompatible with {self.role_1.name}" in form.errors["role"]

    def test_partner_incompatible_roles_edit_exclude_self(self) -> None:
        partner = PartnerFactory()
        partner.allowed_business_areas.add(self.business_area)

        role_assignment = RoleAssignmentFactory(partner=partner, role=self.role_1, business_area=self.business_area)

        # Edit the same assignment
        form = self.form_class(
            data={
                "partner": partner.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            },
            instance=role_assignment,
        )

        # Should be valid because we exclude the current instance
        assert form.is_valid()

    def test_user_compatible_roles_allowed(self) -> None:
        user = UserFactory()

        # User already has role_1
        RoleAssignmentFactory(user=user, role=self.role_1, business_area=self.business_area)

        # Assign role_3 (not incompatible with role_1)
        form = self.form_class(
            data={
                "user": user.id,
                "role": self.role_3.id,
                "business_area": self.business_area.id,
            }
        )

        assert form.is_valid()

    def test_partner_compatible_roles_allowed(self) -> None:
        partner = PartnerFactory()
        partner.allowed_business_areas.add(self.business_area)

        # Partner already has role_1
        RoleAssignmentFactory(partner=partner, role=self.role_1, business_area=self.business_area)

        # Assign role_3 (not incompatible with role_1)
        form = self.form_class(
            data={
                "partner": partner.id,
                "role": self.role_3.id,
                "business_area": self.business_area.id,
            }
        )

        assert form.is_valid()

    def test_user_incompatible_roles_different_business_area_allowed(self) -> None:
        user = UserFactory()
        other_business_area = BusinessAreaFactory(name="Other BA")

        RoleAssignmentFactory(user=user, role=self.role_1, business_area=other_business_area)

        # Assign incompatible role_2 in different business area (should be allowed)
        form = self.form_class(
            data={
                "user": user.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            }
        )

        assert form.is_valid()

    def test_partner_incompatible_roles_different_business_area_allowed(self) -> None:
        partner = PartnerFactory()
        other_business_area = BusinessAreaFactory(name="Other BA")
        partner.allowed_business_areas.add(self.business_area, other_business_area)

        RoleAssignmentFactory(partner=partner, role=self.role_1, business_area=other_business_area)

        # Assign incompatible role_2 in different business area (should be allowed)
        form = self.form_class(
            data={
                "partner": partner.id,
                "role": self.role_2.id,
                "business_area": self.business_area.id,
            }
        )

        assert form.is_valid()


def test_user_privileges_action(django_app: DjangoTestApp, superuser: User) -> None:
    business_area = create_afghanistan()
    user = UserFactory(username="normaluser", is_staff=True)
    role = RoleFactory(name="Test Role")

    RoleAssignmentFactory(
        user=user,
        role=role,
        business_area=business_area,
    )

    url = reverse("admin:account_user_privileges", args=[user.pk])
    res = django_app.get(url, user=superuser)

    assert res.status_code == 200
    assert "permissions" in res.context
    assert "business_ares_permissions" in res.context
    assert res.context["original"] == user


def test_user_privileges_action_shows_user_and_partner_roles(django_app: DjangoTestApp, superuser: User) -> None:
    business_area = create_afghanistan()
    user = UserFactory(username="normaluser", is_staff=True)

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area)
    user.partner = partner
    user.save()

    # Create user role
    user_role = RoleFactory(name="User Role", permissions=["PROGRAM_VIEW_LIST_AND_DETAILS"])
    RoleAssignmentFactory(
        user=user,
        role=user_role,
        business_area=business_area,
    )

    # Create partner role
    partner_role = RoleFactory(name="Partner Role", permissions=["GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE"])
    RoleAssignmentFactory(
        partner=partner,
        role=partner_role,
        business_area=business_area,
    )

    url = reverse("admin:account_user_privileges", args=[user.pk])
    res = django_app.get(url, user=superuser)

    assert res.status_code == 200
    assert "business_ares_permissions" in res.context
    assert business_area.slug in res.context["business_ares_permissions"]

    # Check that permissions from both user and partner roles are present
    ba_permissions = res.context["business_ares_permissions"][business_area.slug]
    assert "PROGRAM_VIEW_LIST_AND_DETAILS" in ba_permissions
    assert "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE" in ba_permissions


@pytest.mark.skip("Fail on pipeline")
class PartnerAdminTest(TestCase):
    def setUp(self) -> None:
        request = RequestFactory()
        self.site = AdminSite()
        self.admin = PartnerAdmin(model=Partner, admin_site=self.site)
        self.request = request.get("/")
        self.request.user = UserFactory(username="testuser", is_staff=True, is_superuser=True)

        self.business_area = create_afghanistan()
        self.unicef = PartnerFactory(name="UNICEF")
        self.unicef_subpartner = PartnerFactory(parent=self.unicef)
        self.parent_partner = PartnerFactory(name="Normal Parent")
        self.partner = PartnerFactory(name="Normal Partner", parent=self.parent_partner)

    def test_get_inline_instances(self) -> None:
        inline_instances = self.admin.get_inline_instances(self.request)
        assert inline_instances == []

        inline_instances = self.admin.get_inline_instances(self.request, self.partner)
        assert len(inline_instances) == 1
        assert isinstance(inline_instances[0], RoleAssignmentInline)

    def test_get_readonly_fields(self) -> None:
        readonly_fields = self.admin.get_readonly_fields(self.request)
        assert readonly_fields == ["sub_partners"]

        readonly_fields = self.admin.get_readonly_fields(self.request, self.partner)
        assert readonly_fields == ["sub_partners"]

        readonly_fields = self.admin.get_readonly_fields(self.request, self.unicef)
        assert readonly_fields == ["sub_partners", "name", "parent"]

        readonly_fields = self.admin.get_readonly_fields(self.request, self.unicef_subpartner)
        assert readonly_fields == ["sub_partners", "name", "parent"]

    def test_get_form_no_obj(self) -> None:
        form = self.admin.get_form(self.request)
        # level 0
        assert self.unicef in form.base_fields["parent"].queryset
        assert self.parent_partner in form.base_fields["parent"].queryset
        # level 1
        assert self.unicef_subpartner not in form.base_fields["parent"].queryset
        assert self.partner not in form.base_fields["parent"].queryset

    def test_get_form_unicef_subpartner(self) -> None:
        form = self.admin.get_form(self.request, self.unicef_subpartner)
        assert "parent" not in form.base_fields

    def test_get_form_unicef(self) -> None:
        form = self.admin.get_form(self.request, self.unicef)
        assert "parent" not in form.base_fields

    def test_get_form_parent_partner(self) -> None:
        form = self.admin.get_form(self.request, self.parent_partner)
        self.assertQuerySetEqual(form.base_fields["parent"].queryset, Partner.objects.none())

    def test_get_form_partner(self) -> None:
        form = self.admin.get_form(self.request, self.partner)
        assert self.unicef in form.base_fields["parent"].queryset
        assert self.parent_partner in form.base_fields["parent"].queryset
        assert self.unicef_subpartner not in form.base_fields["parent"].queryset
        assert self.partner not in form.base_fields["parent"].queryset
