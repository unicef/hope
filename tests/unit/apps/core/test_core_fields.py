from unittest.mock import patch

from hope.apps.core.field_attributes.core_fields_attributes import (
    FieldFactory,
    get_core_fields_attributes,
)
from hope.apps.core.field_attributes.fields_types import TYPE_STRING, Scope


def test_all_core_fields_have_lookup_attribute():
    fields = get_core_fields_attributes()

    missing_lookups = [field.get("name") for field in fields if not field.get("lookup")]

    assert not missing_lookups, f"Fields without lookup: {missing_lookups}"


@patch(
    "hope.apps.core.field_attributes.core_fields_attributes.get_core_fields_attributes",
    lambda: [
        {
            "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce5a4",
            "type": TYPE_STRING,
            "name": "given_name",
            "lookup": "given_name",
            "required": False,
            "label": {"English(EN)": "Given name"},
            "hint": "",
            "choices": [],
            "associated_with": "individual",
            "xlsx_field": "given_name_i_c",
            "scope": [
                Scope.GLOBAL,
                Scope.TARGETING,
                Scope.KOBO_IMPORT,
                Scope.INDIVIDUAL_UPDATE,
                Scope.XLSX_PEOPLE,
            ],
        },
        {
            "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce524",
            "type": TYPE_STRING,
            "name": "given_name1",
            "lookup": "given_name1",
            "required": False,
            "label": {"English(EN)": "Given name1"},
            "hint": "",
            "choices": [],
            "associated_with": "individual",
            "xlsx_field": "given_name1_i_c",
            "scope": [
                Scope.GLOBAL,
                Scope.TARGETING,
                Scope.KOBO_IMPORT,
                Scope.INDIVIDUAL_UPDATE,
            ],
        },
        {
            "id": "36ab3421-6e7a-40d1-b816-ea5cbdcc0b6a",
            "type": TYPE_STRING,
            "name": "full_name",
            "lookup": "full_name",
            "required": True,
            "label": {"English(EN)": "Full name"},
            "hint": "",
            "choices": [],
            "associated_with": "individual",
            "xlsx_field": "full_name_i_c",
            "scope": [Scope.GLOBAL, Scope.XLSX_PEOPLE],
        },
    ],
)
def test_field_factory_filters_by_xlsx_people_scope():
    scopes = [Scope.GLOBAL, Scope.XLSX_PEOPLE]

    result = FieldFactory.from_only_scopes(scopes)

    assert len(result) == 2


@patch(
    "hope.apps.core.field_attributes.core_fields_attributes.get_core_fields_attributes",
    lambda: [
        {
            "id": "b1f90314-b8b8-4bcb-9265-9d48d1fce5a4",
            "type": TYPE_STRING,
            "name": "given_name",
            "lookup": "given_name",
            "required": False,
            "label": {"English(EN)": "Given name"},
            "hint": "",
            "choices": [],
            "associated_with": "individual",
            "xlsx_field": "given_name_i_c",
            "scope": [
                Scope.GLOBAL,
                Scope.TARGETING,
                Scope.KOBO_IMPORT,
                Scope.INDIVIDUAL_UPDATE,
                Scope.XLSX_PEOPLE,
            ],
        }
    ],
)
def test_field_factory_modifies_xlsx_field_for_xlsx_people_scope():
    scopes = [Scope.GLOBAL, Scope.XLSX_PEOPLE]

    result = FieldFactory.from_only_scopes(scopes)

    assert result[0]["xlsx_field"] == "pp_given_name_i_c"


def test_field_factory_returns_all_core_fields_choices():
    choices = FieldFactory.get_all_core_fields_choices()

    assert choices[0] == ("age", "Age (calculated)")
