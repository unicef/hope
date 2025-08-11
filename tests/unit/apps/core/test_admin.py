from typing import List, Optional, Type

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from parameterized import parameterized
from rest_framework import status

from hope.admin.business_area import (
    AcceptanceProcessThresholdFormset,
)
from hope.admin.data_collecting_type import (
    DataCollectingTypeForm,
)
from hope.apps.account.models import RoleAssignment
from hope.apps.core.models import DataCollectingType


class TestAcceptanceProcessThreshold(TestCase):
    @parameterized.expand(
        [
            ([[12, 24]], ValidationError, "Ranges need to start from 0"),
            ([[0, None], [10, 100]], ValidationError, "Provided ranges overlap [0, ∞) [10, 100)"),
            ([[0, 10], [8, 100]], ValidationError, "Provided ranges overlap [0, 10) [8, 100)"),
            (
                [[0, 10], [20, 100]],
                ValidationError,
                "Whole range of [0 , ∞] is not covered, please cover range between [0, 10) [20, 100)",
            ),
            ([[0, 24], [24, 100]], ValidationError, "Last range should cover ∞ (please leave empty value)"),
            ([[0, 24], [24, 100], [100, None]], None, ""),
        ]
    )
    def test_validate_ranges(self, ranges: List[List[Optional[int]]], exc: Optional[Type[Exception]], msg: str) -> None:
        if exc:
            with self.assertRaisesMessage(exc, msg):
                AcceptanceProcessThresholdFormset.validate_ranges(ranges)
        else:
            AcceptanceProcessThresholdFormset.validate_ranges(ranges)


class TestDataCollectingTypeForm(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.form_data = {
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

    def test_type_cannot_be_blank(self) -> None:
        form = DataCollectingTypeForm(self.form_data)

        self.assertFalse(form.is_valid())
        assert form.errors["type"][0] == "This field is required."

    def test_household_filters_cannot_be_marked_when_type_is_social(self) -> None:
        form = DataCollectingTypeForm({**self.form_data, "type": DataCollectingType.Type.SOCIAL})

        self.assertFalse(form.is_valid())
        assert form.errors["type"][0] == "Household filters cannot be applied for data collecting type with social type"

    def test_type_cannot_be_changed_to_different_than_compatible_types(self) -> None:
        social_dct = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
        social_dct_2 = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
        social_dct.compatible_types.add(social_dct)
        social_dct.compatible_types.add(social_dct_2)

        form = DataCollectingTypeForm(
            {
                **self.form_data,
                "type": DataCollectingType.Type.STANDARD,
                "compatible_types": DataCollectingType.objects.filter(id__in=[social_dct.id, social_dct_2.id]),
            },
            instance=social_dct,
        )
        self.assertFalse(form.is_valid())
        assert form.errors["type"][0] == "Type of DCT cannot be changed if it has compatible DCTs of different type"
        assert (
            form.errors["compatible_types"][0] == f"DCTs of different types cannot be compatible with each other."
            f" Following DCTs are not of type STANDARD: ['{str(social_dct_2.label)}']"
        )

    def test_cannot_add_compatible_dct_with_different_type(self) -> None:
        social_dct = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
        standard_dct = DataCollectingTypeFactory(label="Standard DCT", type=DataCollectingType.Type.STANDARD)
        form = DataCollectingTypeForm(
            {
                **self.form_data,
                "type": DataCollectingType.Type.SOCIAL,
                "compatible_types": DataCollectingType.objects.filter(id=standard_dct.id),
            },
            instance=social_dct,
        )
        self.assertFalse(form.is_valid())
        assert (
            form.errors["compatible_types"][0]
            == f"DCTs of different types cannot be compatible with each other. Following DCTs are not of type SOCIAL: ['{str(standard_dct.label)}']"
        )


class BusinessAreaAdminTest(WebTest):
    csrf_checks = False

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory(username="adminuser", is_staff=True, is_superuser=True)
        cls.business_area = create_afghanistan()
        cls.url = reverse("admin:core_businessarea_allowed_partners", args=[cls.business_area.pk])

        cls.partner1 = PartnerFactory(name="Partner 1")
        cls.partner2 = PartnerFactory(name="Partner 2")
        cls.partner3 = PartnerFactory(name="Partner 3")

        RoleAssignment.objects.all().delete()

        cls.partner1.allowed_business_areas.add(cls.business_area)
        cls.partner2.allowed_business_areas.add(cls.business_area)

    def check_initial_state(self) -> None:
        self.assertIn(self.business_area, self.partner1.allowed_business_areas.all())
        self.assertIn(self.business_area, self.partner2.allowed_business_areas.all())
        self.assertNotIn(self.business_area, self.partner3.allowed_business_areas.all())

    def refresh_partners(self) -> None:
        self.partner1.refresh_from_db()
        self.partner2.refresh_from_db()
        self.partner3.refresh_from_db()

    def test_allowed_partners_get_request(self) -> None:
        """Ensure GET request returns a valid response with the correct form"""
        response = self.app.get(self.url, user=self.user)
        assert response.status_code == 200
        self.assertIn("form", response.context)

    def test_allowed_partners_post_request_success(self) -> None:
        self.check_initial_state()
        response = self.app.post(
            self.url,
            user=self.user,
            params={"partners": [self.partner1.id, self.partner3.id]},
        )
        assert response.status_code == status.HTTP_302_FOUND

        self.refresh_partners()
        self.assertIn(self.business_area, self.partner1.allowed_business_areas.all())
        self.assertNotIn(self.business_area, self.partner2.allowed_business_areas.all())  # Removed
        self.assertIn(self.business_area, self.partner3.allowed_business_areas.all())  # Added

    def test_allowed_partners_post_request_prevent_removal_due_to_role_assignment(self) -> None:
        """Ensure a partner with an existing role assignment cannot be removed"""
        self.check_initial_state()

        RoleAssignment.objects.create(partner=self.partner1, business_area=self.business_area)
        response = self.app.post(
            self.url,
            user=self.user,
            params={"partners": [self.partner3.id]},
        )
        assert response.status_code == status.HTTP_302_FOUND

        # Nothing should change
        self.refresh_partners()
        self.check_initial_state()
