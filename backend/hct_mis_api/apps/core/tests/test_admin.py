from typing import List, Optional, Type

from django.core.exceptions import ValidationError
from django.test import TestCase

from parameterized import parameterized

from hct_mis_api.apps.core.admin import (
    AcceptanceProcessThresholdFormset,
    DataCollectingTypeForm,
)
from hct_mis_api.apps.core.models import DataCollectingType


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
        self.assertEqual(form.errors["type"][0], "This field is required.")

    def test_household_filters_cannot_be_marked_when_type_is_social(self) -> None:
        form = DataCollectingTypeForm({**self.form_data, "type": DataCollectingType.Type.SOCIAL})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["type"][0], "Household filters cannot be applied for data collecting type with social type"
        )
