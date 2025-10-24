from django.test import TestCase

from hope.api.endpoints.rdi.lax import HandleFlexFieldsMixin
from hope.apps.core.models import FlexibleAttribute


class TestHandleFlexFieldsMixin(TestCase):
    databases = {"default"}

    def setUp(self) -> None:
        super().setUp()
        self.mixin = HandleFlexFieldsMixin()

        self.individual_flex = FlexibleAttribute.objects.create(
            name="custom_field_i_f",
            label={"English(EN)": "Custom Field"},
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            is_removed=False,
        )

        self.household_flex = FlexibleAttribute.objects.create(
            name="household_field_h_f",
            label={"English(EN)": "Household Field"},
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
            is_removed=False,
        )

        FlexibleAttribute.objects.create(
            name="removed_field_i_f",
            label={"English(EN)": "Removed Field"},
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            is_removed=True,
        )

    def test_get_registered_flex_fields_individual(self) -> None:
        flex_fields = self.mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

        assert "custom_field" in flex_fields
        assert "removed_field" not in flex_fields
        assert len(flex_fields) == 1

    def test_get_registered_flex_fields_household(self) -> None:
        flex_fields = self.mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD)

        assert "household_field" in flex_fields
        assert len(flex_fields) == 1

    def test_get_registered_flex_fields_caching(self) -> None:
        flex_fields_1 = self.mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

        FlexibleAttribute.objects.create(
            name="new_field_i_f",
            label={"English(EN)": "New Field"},
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            is_removed=False,
        )

        flex_fields_2 = self.mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

        assert flex_fields_1 == flex_fields_2
        assert "new_field" not in flex_fields_2

    def test_get_matching_flex_fields(self) -> None:
        candidates = {"custom_field", "unknown_field", "full_name"}

        matching = self.mixin.get_matching_flex_fields(candidates, FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

        assert matching == {"custom_field"}

    def test_handle_individual_flex_fields(self) -> None:
        raw_data = {
            "full_name": "John Doe",
            "custom_field": "custom_value",
            "unknown_field": "unknown_value",
        }

        self.mixin.handle_individual_flex_fields(raw_data)

        assert "custom_field" not in raw_data
        assert "flex_fields" in raw_data
        assert raw_data["flex_fields"] == {"custom_field": "custom_value"}

        assert "full_name" in raw_data

        assert "unknown_field" in raw_data

    def test_handle_household_flex_fields(self) -> None:
        raw_data = {
            "size": 5,
            "household_field": "household_value",
            "unknown_field": "unknown_value",
        }

        self.mixin.handle_household_flex_fields(raw_data)

        assert "household_field" not in raw_data
        assert "flex_fields" in raw_data
        assert raw_data["flex_fields"] == {"household_field": "household_value"}

        assert "size" in raw_data

        assert "unknown_field" in raw_data

    def test_handle_flex_fields_with_reserved_fields(self) -> None:
        raw_data = {
            "full_name": "John Doe",
            "custom_field": "custom_value",
            "documents": [],
        }

        self.mixin.handle_individual_flex_fields(raw_data, reserved_fields={"documents"})

        assert "documents" in raw_data
        assert raw_data["flex_fields"] == {"custom_field": "custom_value"}

    def test_handle_flex_fields_skip_if_already_present(self) -> None:
        raw_data = {
            "full_name": "John Doe",
            "custom_field": "custom_value",
            "flex_fields": {"existing_field": "existing_value"},
        }

        self.mixin.handle_individual_flex_fields(raw_data)

        assert raw_data["flex_fields"] == {"existing_field": "existing_value"}
        assert "custom_field" in raw_data

    def test_handle_flex_fields_empty_raw_data(self) -> None:
        raw_data = {}

        self.mixin.handle_individual_flex_fields(raw_data)

        assert raw_data["flex_fields"] == {}
