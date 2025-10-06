from django.test import TestCase
from django_countries import Countries
import pytest
from rest_framework import serializers

from hope.api.endpoints.rdi.common import DisabilityChoiceField, NullableChoiceField
from hope.apps.household.models import DISABILITY_CHOICES, NOT_DISABLED


class NullableChoiceFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.choices = Countries()
        cls.field = NullableChoiceField(
            choices=cls.choices,
            required=False,
            allow_blank=True,
        )

    def test_blank_converts_to_none(self):
        value = self.field.to_internal_value("")
        assert value is None

    def test_valid_choice_passes(self):
        choice = self.choices[0][0]
        value = self.field.to_internal_value(choice)
        assert value == choice

    def test_invalid_choice_raises(self):
        with pytest.raises(serializers.ValidationError):
            self.field.to_internal_value("invalid_value")


class DisabilityChoiceFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.field = DisabilityChoiceField(
            choices=DISABILITY_CHOICES,
            required=False,
            allow_blank=True,
        )

    def test_blank_converts_to_not_disabled(self):
        value = self.field.to_internal_value("")
        assert value == NOT_DISABLED

    def test_valid_choice_passes(self):
        choice = DISABILITY_CHOICES[0][0]  # take first key from choices
        value = self.field.to_internal_value(choice)
        assert value == choice

    def test_invalid_choice_raises(self):
        with pytest.raises(serializers.ValidationError):
            self.field.to_internal_value("invalid_choice")
