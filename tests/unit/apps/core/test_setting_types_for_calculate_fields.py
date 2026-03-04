from django.conf import settings
from django.core.exceptions import ValidationError
import pytest

from hope.apps.core.field_attributes.fields_types import (
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_STRING,
)
from hope.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hope.models import FlexibleAttribute


@pytest.fixture
def flex_importer():
    return FlexibleAttributeImporter()


def test_import_valid_calculate_types_creates_flex_attributes_with_correct_types(db, flex_importer):
    flex_importer.import_xls(f"{settings.TESTS_ROOT}/apps/core/test_files/flex_init_valid_calculate_types.xlsx")

    expected_flex_fields = [
        ("introduction_h_f", TYPE_STRING),
        ("this_is_date_i_f", TYPE_DATE),
        ("this_is_decimal_h_f", TYPE_DECIMAL),
        ("this_is_integer_i_f", TYPE_INTEGER),
        ("this_is_text_h_f", TYPE_STRING),
    ]
    created_flex_fields = list(FlexibleAttribute.objects.order_by("name").values_list("name", "type"))
    assert created_flex_fields == expected_flex_fields


@pytest.mark.parametrize(
    ("file_name", "expected_error"),
    [
        pytest.param(
            "flex_init_not_existing_calculate_type.xlsx",
            "Survey Sheet: Row 7: Invalid type: not_existing_type for calculate field, "
            "valid choices are text, integer, decimal, date",
            id="non_existing_type",
        ),
        pytest.param(
            "flex_init_empty_calculate_type.xlsx",
            "Survey Sheet: Row 8: Calculated result field type must be provided for calculate type fields",
            id="empty_type",
        ),
        pytest.param(
            "flex_init_space_as_calculate_type.xlsx",
            "Survey Sheet: Row 7: Invalid type:  for calculate field, valid choices are text, integer, decimal, date",
            id="space_as_type",
        ),
    ],
)
def test_import_invalid_calculate_type_raises_validation_error(db, flex_importer, file_name, expected_error):
    with pytest.raises(ValidationError, match=expected_error):
        flex_importer.import_xls(f"{settings.TESTS_ROOT}/apps/core/test_files/{file_name}")
