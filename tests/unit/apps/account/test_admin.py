"""Tests for account admin forms and interfaces."""

from typing import Any
from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.forms.models import inlineformset_factory
from django.test import RequestFactory
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.admin.account_forms import (
    RoleAssignmentAdminForm,
    RoleAssignmentInlineFormSet,
)
from hope.admin.partner import PartnerAdmin
from hope.admin.user_role import PartnerRoleAssignmentAdmin, RoleAssignmentInline, UserRoleAssignmentAdmin
from hope.models import BusinessArea, IncompatibleRoles, Partner, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


def get_mock_request(request_factory: RequestFactory, object_id: Any = None, user: Any = None) -> Any:
    request = request_factory.get("/")
    request.resolver_match = MagicMock()
    request.resolver_match.kwargs = {"object_id": str(object_id) if object_id else None}
    request.user = user if user else MagicMock()
    if not user:
        request.user.can_add_business_area_to_partner = MagicMock(return_value=True)
    return request


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def business_area_ukr(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="ukraine",
        code="4410",
        name="Ukraine",
    )


@pytest.fixture
def role_1(db: Any) -> Role:
    return RoleFactory(name="Role 1")


@pytest.fixture
def unicef_parent(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_subpartner(unicef_parent: Partner) -> Partner:
    return PartnerFactory(parent=unicef_parent)


@pytest.fixture
def role_available_for_partner(db: Any) -> Role:
    return RoleFactory(is_available_for_partner=True)


@pytest.fixture
def role_not_available_for_partner(db: Any) -> Role:
    return RoleFactory(is_available_for_partner=False)


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Partner")


@pytest.fixture
def parent_partner(db: Any) -> Partner:
    """Normal parent partner."""
    return PartnerFactory(name="Parent Partner")


@pytest.fixture
def role_2(db: Any) -> Role:
    return RoleFactory(name="Role_2")


@pytest.fixture
def role_3(db: Any) -> Role:
    return RoleFactory(name="Role_3")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def superuser(db: Any) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def staff_user(db: Any) -> User:
    return UserFactory(is_staff=True)


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def admin_site() -> AdminSite:
    return AdminSite()


def test_role_history(role_1: Role, superuser: User, django_app):
    url = reverse("admin:account_role_change", args=[role_1.pk])
    res = django_app.get(url, user=superuser)

    form = res.forms["role_form"]
    form["permissions"] = ["RDI_VIEW_LIST"]
    form.submit().follow()

    res = django_app.get(url, user=superuser)
    form = res.forms["role_form"]
    form["permissions"] = ["RDI_IMPORT_DATA"]
    form.submit().follow()

    res = django_app.get(url, user=superuser)
    res = res.click("History")
    assert res.status_code == 200


def test_role_matrix(superuser: User, django_app):
    url = reverse("admin:account_role_changelist")
    res = django_app.get(url, user=superuser)
    assert res.click("Matrix").status_code == 200


def test_role_matrix_direct(django_app, superuser: User):
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


def test_user_can_be_assigned_role(role_1: Role, user: User, business_area_afg: BusinessArea):
    data = {
        "role": role_1.id,
        "user": user.id,
        "business_area": business_area_afg.id,
    }
    form = RoleAssignmentAdminForm(data=data)
    assert form.is_valid()


def test_user_cannot_be_assigned_incompatible_role_in_same_business_area(
    role_1: Role,
    role_2: Role,
    user: User,
    business_area_afg: BusinessArea,
):
    # Create incompatible roles relationship
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    # Assign first role to user
    user_role = RoleAssignment.objects.create(
        role=role_1,
        business_area=business_area_afg,
        user=user,
        partner=None,
    )

    # Try to assign incompatible role - should fail
    data = {
        "role": role_2.id,
        "user": user.id,
        "business_area": business_area_afg.id,
    }
    form = RoleAssignmentAdminForm(data=data)
    assert not form.is_valid()
    assert "role" in form.errors
    assert f"This role is incompatible with {role_1.name}" in form.errors["role"]

    # Reverse: change user's role to role_2, then try to assign role_1
    user_role.role = role_2
    user_role.save()
    data["role"] = role_1.id
    form = RoleAssignmentAdminForm(data=data)
    assert not form.is_valid()
    assert "role" in form.errors
    assert f"This role is incompatible with {role_2.name}" in form.errors["role"]


def test_assign_multiple_roles_for_user_at_the_same_time(
    role_1: Role,
    role_2: Role,
    user: User,
    business_area_afg: BusinessArea,
):
    data = {
        "role_assignments-TOTAL_FORMS": "2",
        "role_assignments-INITIAL_FORMS": "0",
        "role_assignments-0-role": role_1.id,
        "role_assignments-1-role": role_2.id,
        "role_assignments-0-business_area": business_area_afg.id,
        "role_assignments-1-business_area": business_area_afg.id,
    }
    RoleAssignmentFormSet = inlineformset_factory(
        User,
        RoleAssignment,
        fields=("__all__"),
        formset=RoleAssignmentInlineFormSet,
    )
    formset = RoleAssignmentFormSet(instance=user, data=data)
    assert formset.is_valid()


def test_assign_multiple_roles_for_user_at_the_same_time_fails_for_incompatible_roles(
    role_1: Role,
    role_2: Role,
    user: User,
    business_area_afg: BusinessArea,
):
    # Create incompatible roles relationship
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    data = {
        "role_assignments-TOTAL_FORMS": "2",
        "role_assignments-INITIAL_FORMS": "0",
        "role_assignments-0-role": role_1.id,
        "role_assignments-1-role": role_2.id,
        "role_assignments-0-business_area": business_area_afg.id,
        "role_assignments-1-business_area": business_area_afg.id,
    }
    RoleAssignmentFormSet = inlineformset_factory(
        User,
        RoleAssignment,
        fields=("__all__"),
        formset=RoleAssignmentInlineFormSet,
    )
    formset = RoleAssignmentFormSet(instance=user, data=data)
    assert not formset.is_valid()
    assert len(formset.errors) == 2

    # Check that incompatibility error is present
    errors = formset.errors
    role_errors = errors[0]["role"]
    assert f"{role_1.name} is incompatible with {role_2.name}." in role_errors


def test_role_assignment_inline_formfield_for_foreignkey_business_area(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    business_area_afg: BusinessArea,
    business_area_ukr: BusinessArea,
    unicef_subpartner: Partner,
):
    admin = RoleAssignmentInline(parent_model=Partner, admin_site=admin_site)
    unicef_subpartner.allowed_business_areas.add(business_area_afg)

    request = get_mock_request(request_factory, object_id=unicef_subpartner.id)

    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
    assert business_area_afg in field.queryset
    assert business_area_ukr not in field.queryset

    # Mock request without valid object_id
    request = get_mock_request(request_factory, object_id="some not digit string")
    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
    assert business_area_afg in field.queryset
    assert business_area_ukr in field.queryset


def test_role_assignment_inline_formfield_for_foreignkey_role(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    unicef_subpartner: Partner,
    role_available_for_partner: Role,
    role_not_available_for_partner: Role,
):
    admin = RoleAssignmentInline(parent_model=Partner, admin_site=admin_site)

    request = get_mock_request(request_factory, object_id=unicef_subpartner.id)

    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
    assert role_available_for_partner in field.queryset
    assert role_not_available_for_partner not in field.queryset

    # Mock request without valid object_id
    request = get_mock_request(request_factory, object_id="some not digit string")
    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
    assert role_available_for_partner in field.queryset
    assert role_not_available_for_partner in field.queryset


def test_role_assignment_inline_has_permissions(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    user: User,
    superuser: User,
    unicef_parent: Partner,
    unicef_subpartner: Partner,
):
    admin = RoleAssignmentInline(parent_model=Partner, admin_site=admin_site)
    partner_without_parent = PartnerFactory(parent=None, name="Parent without parent")

    request = get_mock_request(request_factory, object_id=unicef_subpartner.id, user=superuser)

    assert admin.has_add_permission(request, unicef_subpartner)
    assert admin.has_add_permission(request, partner_without_parent)
    assert admin.has_add_permission(request, user)

    assert admin.has_change_permission(request, unicef_subpartner)
    assert admin.has_change_permission(request, unicef_parent)
    assert admin.has_change_permission(request, partner_without_parent)
    assert admin.has_change_permission(request, user)

    assert admin.has_delete_permission(request, unicef_subpartner)
    assert admin.has_delete_permission(request, unicef_parent)
    assert admin.has_delete_permission(request, partner_without_parent)
    assert admin.has_delete_permission(request, user)


def test_user_role_assignment_admin_get_queryset(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
):
    admin = UserRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    user_role_assignment = RoleAssignmentFactory(
        user=staff_user,
        partner=None,
        role=role_1,
        business_area=business_area_afg,
    )

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)
    partner_role_assignment = RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role_1,
        business_area=business_area_afg,
    )

    request = get_mock_request(request_factory, user=staff_user)
    queryset = admin.get_queryset(request)

    # Should only include user role assignments
    assert user_role_assignment in queryset
    assert partner_role_assignment not in queryset


def test_user_role_assignment_admin_get_fields(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
):
    admin = UserRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    request = get_mock_request(request_factory, user=staff_user)
    fields = admin.get_fields(request)

    assert "user" in fields
    assert "partner" not in fields
    assert "business_area" in fields
    assert "program" in fields
    assert "role" in fields
    assert "expiry_date" in fields
    assert "group" in fields


def test_user_role_assignment_admin_permissions(
    request_factory: RequestFactory,
    admin_site: AdminSite,
):
    admin = UserRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    user_with_perm = UserFactory(is_staff=True)
    for permission in [
        "view_roleassignment",
        "add_roleassignment",
        "change_roleassignment",
        "delete_roleassignment",
    ]:
        user_with_perm.user_permissions.add(Permission.objects.get(codename=permission))

    user_without_perm = UserFactory(is_staff=True)

    request_with_perm = get_mock_request(request_factory, user=user_with_perm)
    request_without_perm = get_mock_request(request_factory, user=user_without_perm)

    # With permission
    assert admin.has_module_permission(request_with_perm)
    assert admin.has_view_permission(request_with_perm)
    assert admin.has_add_permission(request_with_perm)
    assert admin.has_change_permission(request_with_perm)
    assert admin.has_delete_permission(request_with_perm)

    # Without permission
    assert not admin.has_module_permission(request_without_perm)
    assert not admin.has_view_permission(request_without_perm)
    assert not admin.has_add_permission(request_without_perm)
    assert not admin.has_change_permission(request_without_perm)
    assert not admin.has_delete_permission(request_without_perm)


def test_partner_role_assignment_admin_get_queryset(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
):
    admin = PartnerRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)
    partner_role_assignment = RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=role_1,
        business_area=business_area_afg,
    )

    user_role_assignment = RoleAssignmentFactory(
        user=staff_user,
        partner=None,
        role=role_1,
        business_area=business_area_afg,
    )

    request = get_mock_request(request_factory, user=staff_user)
    queryset = admin.get_queryset(request)

    # Should only include partner role assignments
    assert partner_role_assignment in queryset
    assert user_role_assignment not in queryset


def test_partner_role_assignment_admin_get_fields(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
):
    admin = PartnerRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    request = get_mock_request(request_factory, user=staff_user)
    fields = admin.get_fields(request)

    assert "partner" in fields
    assert "user" not in fields
    assert "business_area" in fields
    assert "program" in fields
    assert "role" in fields
    assert "expiry_date" in fields
    assert "group" in fields


def test_partner_role_assignment_admin_formfield_for_foreignkey_role_filters_partner_available(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
    role_available_for_partner: Role,
    role_not_available_for_partner: Role,
):
    admin = PartnerRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    request = get_mock_request(request_factory, user=staff_user)

    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)

    # Should only show roles available for partners
    assert role_available_for_partner in field.queryset
    assert role_not_available_for_partner not in field.queryset


def test_partner_role_assignment_admin_formfield_for_foreignkey_business_area_filters_split(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    staff_user: User,
    business_area_afg: BusinessArea,
):
    admin = PartnerRoleAssignmentAdmin(model=RoleAssignment, admin_site=admin_site)

    business_area_split = BusinessAreaFactory(name="Split BA", is_split=True)

    request = get_mock_request(request_factory, user=staff_user)

    field = admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)

    # Should exclude split business areas
    assert business_area_afg in field.queryset
    assert business_area_split not in field.queryset


def test_role_assignment_admin_form_user_incompatible_roles_create(
    user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    # User already has role_1
    RoleAssignmentFactory(user=user, partner=None, role=role_1, business_area=business_area_afg)

    # Try to assign incompatible role_2
    form = RoleAssignmentAdminForm(
        data={
            "user": user.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        }
    )

    assert not form.is_valid()
    assert "role" in form.errors
    assert f"This role is incompatible with {role_1.name}" in form.errors["role"]


def test_role_assignment_admin_form_user_incompatible_roles_edit_exclude_self(
    user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    role_assignment = RoleAssignmentFactory(user=user, partner=None, role=role_1, business_area=business_area_afg)

    # Edit the same assignment - should be valid because we exclude the current instance
    form = RoleAssignmentAdminForm(
        data={
            "user": user.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        },
        instance=role_assignment,
    )

    assert form.is_valid()


def test_role_assignment_admin_form_partner_incompatible_roles_create(
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)

    RoleAssignmentFactory(user=None, partner=partner, role=role_1, business_area=business_area_afg)

    # Try to assign incompatible role_2
    form = RoleAssignmentAdminForm(
        data={
            "partner": partner.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        }
    )

    assert not form.is_valid()
    assert "role" in form.errors
    assert f"This role is incompatible with {role_1.name}" in form.errors["role"]


def test_role_assignment_admin_form_partner_incompatible_roles_edit_exclude_self(
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)

    role_assignment = RoleAssignmentFactory(user=None, partner=partner, role=role_1, business_area=business_area_afg)

    # Edit the same assignment - should be valid because we exclude the current instance
    form = RoleAssignmentAdminForm(
        data={
            "partner": partner.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        },
        instance=role_assignment,
    )

    assert form.is_valid()


def test_role_assignment_admin_form_user_compatible_roles_allowed(
    user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
    role_3: Role,
):
    # User already has role_1
    RoleAssignmentFactory(user=user, partner=None, role=role_1, business_area=business_area_afg)

    # Assign role_3 (not incompatible with role_1)
    form = RoleAssignmentAdminForm(
        data={
            "user": user.id,
            "role": role_3.id,
            "business_area": business_area_afg.id,
        }
    )

    assert form.is_valid()


def test_role_assignment_admin_form_partner_compatible_roles_allowed(
    business_area_afg: BusinessArea,
    role_1: Role,
    role_3: Role,
):
    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)

    # Partner already has role_1
    RoleAssignmentFactory(user=None, partner=partner, role=role_1, business_area=business_area_afg)

    # Assign role_3 (not incompatible with role_1)
    form = RoleAssignmentAdminForm(
        data={
            "partner": partner.id,
            "role": role_3.id,
            "business_area": business_area_afg.id,
        }
    )

    assert form.is_valid()


def test_role_assignment_admin_form_user_incompatible_roles_different_business_area_allowed(
    user: User,
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    other_business_area = BusinessAreaFactory(name="Other BA")

    RoleAssignmentFactory(user=user, partner=None, role=role_1, business_area=other_business_area)

    # Assign incompatible role_2 in different business area (should be allowed)
    form = RoleAssignmentAdminForm(
        data={
            "user": user.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        }
    )

    assert form.is_valid()


def test_role_assignment_admin_form_partner_incompatible_roles_different_business_area_allowed(
    business_area_afg: BusinessArea,
    role_1: Role,
    role_2: Role,
):
    IncompatibleRoles.objects.create(role_one=role_1, role_two=role_2)

    partner = PartnerFactory()
    other_business_area = BusinessAreaFactory(name="Other BA")
    partner.allowed_business_areas.add(business_area_afg, other_business_area)

    RoleAssignmentFactory(user=None, partner=partner, role=role_1, business_area=other_business_area)

    # Assign incompatible role_2 in different business area (should be allowed)
    form = RoleAssignmentAdminForm(
        data={
            "partner": partner.id,
            "role": role_2.id,
            "business_area": business_area_afg.id,
        }
    )

    assert form.is_valid()


def test_user_privileges_action(django_app, superuser: User, business_area_afg: BusinessArea):
    user = UserFactory(is_staff=True)
    role = RoleFactory(name="Test Role")

    RoleAssignmentFactory(
        user=user,
        partner=None,
        role=role,
        business_area=business_area_afg,
    )

    url = reverse("admin:account_user_privileges", args=[user.pk])
    res = django_app.get(url, user=superuser)

    assert res.status_code == 200
    assert "permissions" in res.context
    assert "business_ares_permissions" in res.context
    assert res.context["original"] == user


def test_user_privileges_action_shows_user_and_partner_roles(
    django_app,
    superuser: User,
    business_area_afg: BusinessArea,
):
    user = UserFactory(is_staff=True)

    partner = PartnerFactory()
    partner.allowed_business_areas.add(business_area_afg)
    user.partner = partner
    user.save()

    # Create user role
    user_role = RoleFactory(name="User Role", permissions=["PROGRAM_VIEW_LIST_AND_DETAILS"])
    RoleAssignmentFactory(
        user=user,
        partner=None,
        role=user_role,
        business_area=business_area_afg,
    )

    # Create partner role
    partner_role = RoleFactory(name="Partner Role", permissions=["GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE"])
    RoleAssignmentFactory(
        user=None,
        partner=partner,
        role=partner_role,
        business_area=business_area_afg,
    )

    url = reverse("admin:account_user_privileges", args=[user.pk])
    res = django_app.get(url, user=superuser)

    assert res.status_code == 200
    assert "business_ares_permissions" in res.context
    assert business_area_afg.slug in res.context["business_ares_permissions"]

    # Check that permissions from both user and partner roles are present
    ba_permissions = res.context["business_ares_permissions"][business_area_afg.slug]
    assert "PROGRAM_VIEW_LIST_AND_DETAILS" in ba_permissions
    assert "GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE" in ba_permissions


def test_partner_admin_get_inline_instances(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    superuser: User,
    partner: Partner,
):
    admin = PartnerAdmin(model=Partner, admin_site=admin_site)

    request = get_mock_request(request_factory, user=superuser)

    # No obj - should return empty list
    inline_instances = admin.get_inline_instances(request)
    assert inline_instances == []

    # With partner obj - should return RoleAssignmentInline
    inline_instances = admin.get_inline_instances(request, partner)
    assert len(inline_instances) == 1
    assert isinstance(inline_instances[0], RoleAssignmentInline)


def test_partner_admin_get_readonly_fields(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    superuser: User,
    unicef_parent: Partner,
    unicef_subpartner: Partner,
    partner: Partner,
):
    admin = PartnerAdmin(model=Partner, admin_site=admin_site)

    request = get_mock_request(request_factory, user=superuser)

    # No obj
    readonly_fields = admin.get_readonly_fields(request)
    assert readonly_fields == ["sub_partners"]

    # Normal partner
    readonly_fields = admin.get_readonly_fields(request, partner)
    assert readonly_fields == ["sub_partners"]

    # UNICEF
    readonly_fields = admin.get_readonly_fields(request, unicef_parent)
    assert readonly_fields == ["sub_partners", "name", "parent"]

    # UNICEF subpartner
    readonly_fields = admin.get_readonly_fields(request, unicef_subpartner)
    assert readonly_fields == ["sub_partners", "name", "parent"]


def test_partner_admin_get_form(
    request_factory: RequestFactory,
    admin_site: AdminSite,
    superuser: User,
    unicef_parent: Partner,
    unicef_subpartner: Partner,
    parent_partner: Partner,
):
    admin = PartnerAdmin(model=Partner, admin_site=admin_site)

    request = get_mock_request(request_factory, user=superuser)

    partner = PartnerFactory(name="Normal Partner", parent=parent_partner)

    # No obj - level 0 partners should be in queryset, level 1 should not
    form = admin.get_form(request)
    assert unicef_parent in form.base_fields["parent"].queryset
    assert parent_partner in form.base_fields["parent"].queryset
    assert unicef_subpartner not in form.base_fields["parent"].queryset
    assert partner not in form.base_fields["parent"].queryset

    # UNICEF subpartner - parent field should not be in form
    form = admin.get_form(request, unicef_subpartner)
    assert "parent" not in form.base_fields

    # UNICEF - parent field should not be in form
    form = admin.get_form(request, unicef_parent)
    assert "parent" not in form.base_fields

    # Parent partner - parent queryset should be empty
    form = admin.get_form(request, parent_partner)
    assert list(form.base_fields["parent"].queryset) == []

    # Normal partner - level 0 partners in queryset, not itself or other level 1
    form = admin.get_form(request, partner)
    assert unicef_parent in form.base_fields["parent"].queryset
    assert parent_partner in form.base_fields["parent"].queryset
    assert unicef_subpartner not in form.base_fields["parent"].queryset
    assert partner not in form.base_fields["parent"].queryset
