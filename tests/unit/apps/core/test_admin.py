import re
from typing import TYPE_CHECKING
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.admin.business_area import AcceptanceProcessThresholdFormset
from hope.admin.data_collecting_type import DataCollectingTypeForm
from hope.models import DataCollectingType

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp

pytestmark = pytest.mark.django_db


# === AcceptanceProcessThreshold Tests ===


@pytest.mark.parametrize(
    ("ranges", "expected_error"),
    [
        ([[12, 24]], "Ranges need to start from 0"),
        ([[0, None], [10, 100]], "Provided ranges overlap [0, ∞) [10, 100)"),
        ([[0, 10], [8, 100]], "Provided ranges overlap [0, 10) [8, 100)"),
        ([[0, 10], [20, 100]], "Whole range of [0 , ∞] is not covered, please cover range between [0, 10) [20, 100)"),
        ([[0, 24], [24, 100]], "Last range should cover ∞ (please leave empty value)"),
    ],
)
def test_acceptance_threshold_formset_rejects_invalid_ranges(ranges, expected_error):
    with pytest.raises(ValidationError, match=re.escape(expected_error)):
        AcceptanceProcessThresholdFormset.validate_ranges(ranges)


def test_acceptance_threshold_formset_accepts_valid_ranges():
    AcceptanceProcessThresholdFormset.validate_ranges([[0, 24], [24, 100], [100, None]])


# === DataCollectingTypeForm Tests ===


@pytest.fixture
def dct_form_data():
    return {
        "label": "dct",
        "code": "dct",
        "description": "",
        "compatible_types": "",
        "limit_to": "",
        "active": True,
        "deprecated": False,
        "individual_filters_available": False,
        "household_filters_available": True,
        "recalculate_composition": False,
        "weight": 0,
    }


def test_dct_form_requires_type_field(dct_form_data):
    form = DataCollectingTypeForm(dct_form_data)

    assert not form.is_valid()
    assert form.errors["type"][0] == "This field is required."


def test_dct_form_rejects_household_filters_for_social_type(dct_form_data):
    form = DataCollectingTypeForm({**dct_form_data, "type": DataCollectingType.Type.SOCIAL})

    assert not form.is_valid()
    assert form.errors["type"][0] == "Household filters cannot be applied for data collecting type with social type"


@pytest.fixture
def social_dcts():
    social_dct = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
    social_dct_2 = DataCollectingTypeFactory(label="Social DCT 2", type=DataCollectingType.Type.SOCIAL)
    social_dct.compatible_types.add(social_dct)
    social_dct.compatible_types.add(social_dct_2)
    return social_dct, social_dct_2


def test_dct_form_rejects_type_change_when_incompatible_with_existing_dcts(dct_form_data, social_dcts):
    social_dct, social_dct_2 = social_dcts
    form = DataCollectingTypeForm(
        {
            **dct_form_data,
            "type": DataCollectingType.Type.STANDARD,
            "compatible_types": DataCollectingType.objects.filter(id__in=[social_dct.id, social_dct_2.id]),
        },
        instance=social_dct,
    )

    assert not form.is_valid()
    assert form.errors["type"][0] == "Type of DCT cannot be changed if it has compatible DCTs of different type"
    assert (
        form.errors["compatible_types"][0] == f"DCTs of different types cannot be compatible with each other."
        f" Following DCTs are not of type STANDARD: ['{str(social_dct_2.label)}']"
    )


@pytest.fixture
def mixed_type_dcts():
    social_dct = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
    standard_dct = DataCollectingTypeFactory(label="Standard DCT", type=DataCollectingType.Type.STANDARD)
    return social_dct, standard_dct


def test_dct_form_rejects_compatible_dct_with_different_type(dct_form_data, mixed_type_dcts):
    social_dct, standard_dct = mixed_type_dcts
    form = DataCollectingTypeForm(
        {
            **dct_form_data,
            "type": DataCollectingType.Type.SOCIAL,
            "compatible_types": DataCollectingType.objects.filter(id=standard_dct.id),
        },
        instance=social_dct,
    )

    assert not form.is_valid()
    assert (
        form.errors["compatible_types"][0]
        == f"DCTs of different types cannot be compatible with each other. Following DCTs are not of type SOCIAL: "
        f"['{str(standard_dct.label)}']"
    )


# === BusinessArea Admin Tests ===


@pytest.fixture
def admin_user():
    return UserFactory(username="adminuser", is_staff=True, is_superuser=True)


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def partners_with_access(business_area):
    from hope.models import RoleAssignment

    RoleAssignment.objects.all().delete()
    partner1 = PartnerFactory(name="Partner 1")
    partner2 = PartnerFactory(name="Partner 2")
    partner3 = PartnerFactory(name="Partner 3")
    partner1.allowed_business_areas.add(business_area)
    partner2.allowed_business_areas.add(business_area)
    return partner1, partner2, partner3


def test_business_area_admin_allowed_partners_returns_form(django_app: "DjangoTestApp", admin_user, business_area):
    url = reverse("admin:core_businessarea_allowed_partners", args=[business_area.pk])

    response = django_app.get(url, user=admin_user)

    assert response.status_code == 200
    assert "form" in response.context


def test_business_area_admin_allowed_partners_updates_access(
    django_app: "DjangoTestApp", admin_user, business_area, partners_with_access
):
    partner1, partner2, partner3 = partners_with_access
    url = reverse("admin:core_businessarea_allowed_partners", args=[business_area.pk])
    get_response = django_app.get(url, user=admin_user)
    form = list(get_response.forms.values())[-1]
    form["partners"].force_value([str(partner1.id), str(partner3.id)])

    response = form.submit()

    assert response.status_code == status.HTTP_302_FOUND
    partner1.refresh_from_db()
    partner2.refresh_from_db()
    partner3.refresh_from_db()
    assert business_area in partner1.allowed_business_areas.all()
    assert business_area not in partner2.allowed_business_areas.all()
    assert business_area in partner3.allowed_business_areas.all()


@pytest.fixture
def partner1_with_role_assignment(business_area, partners_with_access):
    partner1, _, _ = partners_with_access
    RoleAssignmentFactory(partner=partner1, business_area=business_area)
    return partner1


def test_business_area_admin_prevents_partner_removal_with_role_assignment(
    django_app: "DjangoTestApp", admin_user, business_area, partners_with_access, partner1_with_role_assignment
):
    partner1, partner2, partner3 = partners_with_access
    url = reverse("admin:core_businessarea_allowed_partners", args=[business_area.pk])
    get_response = django_app.get(url, user=admin_user)
    form = list(get_response.forms.values())[-1]
    form["partners"].force_value([str(partner3.id)])

    response = form.submit()

    assert response.status_code == status.HTTP_302_FOUND
    partner1.refresh_from_db()
    partner2.refresh_from_db()
    partner3.refresh_from_db()
    assert business_area in partner1.allowed_business_areas.all()
    assert business_area in partner2.allowed_business_areas.all()
    assert business_area not in partner3.allowed_business_areas.all()


# === Role Admin Tests ===


@pytest.fixture
def superuser():
    return UserFactory(is_superuser=True)


@pytest.fixture
def role():
    return RoleFactory(name="Test Role")


@pytest.fixture
def role_assignment_for_partner(business_area):
    partner = PartnerFactory(name="Partner with Assignment")
    return RoleAssignmentFactory(partner=partner, business_area=business_area)


def test_role_admin_members_redirects_to_user_role_assignment_list(client, superuser, role):
    client.force_login(superuser, "django.contrib.auth.backends.ModelBackend")
    url = reverse("admin:account_role_members", args=[role.pk])

    with patch.object(type(superuser), "has_perm", return_value=True):
        response = client.get(url)

    expected_url = reverse("admin:account_userroleassignment_changelist") + f"?role__id__exact={role.pk}"
    assert response.status_code == 302
    assert response.url == expected_url
