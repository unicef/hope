"""Tests for user import CSV and Kobo user actions."""

from pathlib import Path
from typing import Any

from django.conf import settings
from django.urls import reverse
from django_webtest import WebTest
import pytest
import responses

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.models import BusinessArea, IncompatibleRoles, Partner, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        code="0060",
        slug="afghanistan",
        name="Afghanistan",
    )


@pytest.fixture
def superuser_staff(db: Any) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def role_no_access(db: Any) -> Role:
    return RoleFactory(name="NoAccess")


@pytest.fixture
def role_2(db: Any) -> Role:
    return RoleFactory(name="Role_2")


@pytest.fixture
def partner_1(db: Any) -> Partner:
    return PartnerFactory(name="Partner1")


@pytest.fixture
def incompatible_roles_setup(role_no_access: Role, role_2: Role) -> None:
    IncompatibleRoles.objects.create(role_one=role_no_access, role_two=role_2)


@responses.activate
def test_import_csv_creates_user(
    django_app: WebTest,
    superuser_staff: User,
    business_area_afghanistan: BusinessArea,
    partner_1: Partner,
    role_no_access: Role,
    incompatible_roles_setup: None,
):
    url = reverse("admin:account_user_import_csv")

    res = django_app.get(url, user=superuser_staff)
    form = res.forms["load_users"]
    form["file"] = (
        "users.csv",
        (Path(__file__).parent / "users.csv").read_bytes(),
    )
    form["business_area"] = business_area_afghanistan.id
    form["partner"] = partner_1.id
    form["role"] = role_no_access.id
    res = form.submit()

    assert res.status_code == 200
    user = User.objects.filter(email="test@example.com", partner=partner_1).first()
    assert user, "User not found"


@responses.activate
def test_import_csv_with_kobo_creates_user_with_kobo_username(
    django_app: WebTest,
    superuser_staff: User,
    business_area_afghanistan: BusinessArea,
    partner_1: Partner,
    role_no_access: Role,
    incompatible_roles_setup: None,
):
    responses.add(
        responses.POST,
        f"{settings.KOBO_URL}/authorized_application/users/",
        json={},
        status=201,
    )
    url = reverse("admin:account_user_import_csv")

    res = django_app.get(url, user=superuser_staff)
    form = res.forms["load_users"]
    form["file"] = (
        "users.csv",
        (Path(__file__).parent / "users.csv").read_bytes(),
    )
    form["business_area"] = business_area_afghanistan.id
    form["partner"] = partner_1.id
    form["role"] = role_no_access.id
    res = form.submit()

    assert res.status_code == 200
    user = User.objects.filter(email="test@example.com", partner=partner_1).first()
    assert user, "User not found"


@responses.activate
def test_import_csv_detect_incompatible_roles_prevents_assignment(
    django_app: WebTest,
    superuser_staff: User,
    business_area_afghanistan: BusinessArea,
    partner_1: Partner,
    role_no_access: Role,
    role_2: Role,
    incompatible_roles_setup: None,
):
    user = UserFactory(email="test@example.com", partner=partner_1)
    RoleAssignmentFactory(user=user, role=role_2, business_area=business_area_afghanistan)
    url = reverse("admin:account_user_import_csv")

    res = django_app.get(url, user=superuser_staff)
    form = res.forms["load_users"]
    form["file"] = (
        "users.csv",
        (Path(__file__).parent / "users.csv").read_bytes(),
    )
    form["business_area"] = business_area_afghanistan.id
    form["partner"] = partner_1.id
    form["role"] = role_no_access.id
    res = form.submit()

    assert res.status_code == 200
    assert not user.role_assignments.filter(role=role_no_access, business_area=business_area_afghanistan).exists()


@responses.activate
def test_import_csv_does_not_change_existing_partner(
    django_app: WebTest,
    superuser_staff: User,
    business_area_afghanistan: BusinessArea,
    partner_1: Partner,
    role_no_access: Role,
    incompatible_roles_setup: None,
):
    partner2 = PartnerFactory(name="Partner2")
    UserFactory(email="test@example.com", partner=partner_1)
    url = reverse("admin:account_user_import_csv")

    res = django_app.get(url, user=superuser_staff)
    form = res.forms["load_users"]
    form["file"] = (
        "users.csv",
        (Path(__file__).parent / "users.csv").read_bytes(),
    )
    form["business_area"] = business_area_afghanistan.id
    form["partner"] = partner2.id
    form["role"] = role_no_access.id
    res = form.submit()

    assert res.status_code == 200
    assert not User.objects.filter(email="test@example.com", partner=partner2).exists()


@responses.activate
def test_import_csv_with_username_creates_user_with_custom_username(
    django_app: WebTest,
    superuser_staff: User,
    business_area_afghanistan: BusinessArea,
    partner_1: Partner,
    role_no_access: Role,
    incompatible_roles_setup: None,
):
    url = reverse("admin:account_user_import_csv")

    res = django_app.get(url, user=superuser_staff)
    form = res.forms["load_users"]
    form["file"] = (
        "users2.csv",
        (Path(__file__).parent / "users2.csv").read_bytes(),
    )
    form["business_area"] = business_area_afghanistan.id
    form["partner"] = partner_1.id
    form["role"] = role_no_access.id
    res = form.submit()

    assert res.status_code == 200
    assert User.objects.filter(email="test@example.com", username="test_example1", partner=partner_1).exists()
