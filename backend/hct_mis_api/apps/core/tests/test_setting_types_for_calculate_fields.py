from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from parameterized import parameterized

from hct_mis_api.apps.core.field_attributes.fields_types import (
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_STRING,
)
from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hct_mis_api.apps.core.models import FlexibleAttribute


class MockSuperUser:
    def has_perm(self, perm):
        return True


class TestSettingTypesForCalculateFields(TestCase):
    @staticmethod
    def load_xls_file(name):
        task = FlexibleAttributeImporter()
        task.import_xls(f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/{name}")

    @parameterized.expand(
        [
            (
                "valid_file",
                "flex_init_valid_calculate_types.xlsx",
                None,
            ),
            (
                "invalid_file",
                "flex_init_not_existing_calculate_type.xlsx",
                "Survey Sheet: Row 8: Invalid type: not_existing_type for calculate field, "
                "valid choices are text, integer, decimal, date",
            ),
            (
                "invalid_file",
                "flex_init_empty_calculate_type.xlsx",
                "Survey Sheet: Row 9: Calculated result field type must be provided for calculate type fields",
            ),
            (
                "invalid_file",
                "flex_init_space_as_calculate_type.xlsx",
                "Survey Sheet: Row 8: Invalid type:  for calculate field, "
                "valid choices are text, integer, decimal, date",
            ),
        ]
    )
    def test_setting_calculate_field_types(self, _, file_name, validation_error):
        if validation_error is not None:
            self.assertRaisesMessage(
                ValidationError,
                validation_error,
                self.load_xls_file,
                file_name,
            )
        else:
            self.load_xls_file(file_name)

            expected_flex_fields = [
                ("introduction_h_f", TYPE_STRING),
                ("this_is_date_i_f", TYPE_DATE),
                ("this_is_decimal_h_f", TYPE_DECIMAL),
                ("this_is_integer_i_f", TYPE_INTEGER),
                ("this_is_text_h_f", TYPE_STRING),
            ]
            created_flex_fields = list(FlexibleAttribute.objects.order_by("name").values_list("name", "type"))
            self.assertEqual(created_flex_fields, expected_flex_fields)
