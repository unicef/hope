"""Tests for RdiXlsxCreateTask extracted helper methods."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from extras.test_utils.factories import RegistrationDataImportFactory
from hope.apps.household.const import HEAD
from hope.apps.registration_data.tasks.rdi_xlsx_create import RdiXlsxCreateTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def task():
    return RdiXlsxCreateTask()


@pytest.fixture
def rdi():
    return RegistrationDataImportFactory()


def _make_header_cells(names: list[str]) -> list:
    cells = []
    for name in names:
        cell = MagicMock()
        cell.value = name
        cells.append(cell)
    return cells


# --- _find_header_indices ---


def test_find_header_indices_both_present(task):
    first_row = _make_header_cells(["name", "household_id", "age", "relationship_i_c"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx == 1
    assert rel_idx == 3


def test_find_header_indices_none_present(task):
    first_row = _make_header_cells(["name", "age", "sex"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx is None
    assert rel_idx is None


def test_find_header_indices_only_household_id(task):
    first_row = _make_header_cells(["household_id", "name"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx == 0
    assert rel_idx is None


# --- _should_skip_cell ---


def test_should_skip_cell_pdu_column(task):
    with patch.object(
        type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=["pdu_field_round_1_value"]
    ):
        result = task._should_skip_cell(
            "pdu_field_round_1_value", "val", {"type": "STRING"}, {"individuals": {}}, "individuals"
        )
    assert result is True


def test_should_skip_cell_excluded_age(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell("age", "25", {"type": "INTEGER"}, {"individuals": {}}, "individuals")
    assert result is True


def test_should_skip_cell_not_in_field_or_complex(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell("unknown_header", "val", {}, {"individuals": {}}, "individuals")
    assert result is True


def test_should_skip_cell_not_required_empty_non_image(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "some_field",
            None,
            {"type": "STRING", "required": False},
            {"individuals": {"some_field": lambda **kw: None}},
            "individuals",
        )
    assert result is True


def test_should_skip_cell_required_field_not_skipped(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "some_field", "value", {"type": "STRING", "required": True}, {"individuals": {}}, "individuals"
        )
    assert result is False


def test_should_skip_cell_image_type_not_skipped_when_empty(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "photo_field", None, {"type": "IMAGE", "required": False}, {"individuals": {}}, "individuals"
        )
    assert result is False


# --- _process_complex_field ---


def test_process_complex_field_not_in_complex_fields(task):
    result = task._process_complex_field(
        "regular_field", "value", MagicMock(), MagicMock(), {"individuals": {}}, "individuals", {}, {}
    )
    assert result is False


def test_process_complex_field_calls_handler_and_sets_attr(task):
    handler = MagicMock(return_value="processed_value")
    obj = MagicMock()
    cell = MagicMock()
    cell.row = 5

    complex_fields = {"individuals": {"special_field": handler}}
    combined_fields = {"special_field": {"name": "target_attr"}}
    current_field = {"required": True}

    result = task._process_complex_field(
        "special_field", "raw_value", cell, obj, complex_fields, "individuals", current_field, combined_fields
    )
    assert result is True
    handler.assert_called_once()
    assert obj.target_attr == "processed_value"


def test_process_complex_field_handler_returns_none_no_setattr(task):
    handler = MagicMock(return_value=None)
    obj = MagicMock(spec=[])  # no attributes
    cell = MagicMock()
    cell.row = 5

    complex_fields = {"individuals": {"field": handler}}
    combined_fields = {"field": {"name": "attr"}}

    result = task._process_complex_field("field", "val", cell, obj, complex_fields, "individuals", {}, combined_fields)
    assert result is True
    assert not hasattr(obj, "attr")


# --- _process_regular_field ---


def test_process_regular_field_household_id_returns_false(task):
    obj = MagicMock()
    combined_fields = {"household_id": {"name": "household_id"}}
    result = task._process_regular_field("household_id", "val", MagicMock(), obj, combined_fields)
    assert result is False


def test_process_regular_field_no_attribute_returns_false(task):
    obj = MagicMock(spec=[])
    combined_fields = {"some_field": {"name": "nonexistent_attr"}}
    result = task._process_regular_field("some_field", "val", MagicMock(), obj, combined_fields)
    assert result is False


def test_process_regular_field_none_value_returns_true(task):
    obj = MagicMock()
    obj.some_attr = "old"
    combined_fields = {"some_field": {"name": "some_attr"}}
    result = task._process_regular_field("some_field", None, MagicMock(), obj, combined_fields)
    assert result is True


# --- _create_pending_object_factory ---


def test_create_pending_object_factory_households(task, rdi):
    factory = task._create_pending_object_factory("households", rdi)
    assert callable(factory)


def test_create_pending_object_factory_individuals(task, rdi):
    factory = task._create_pending_object_factory("individuals", rdi)
    assert callable(factory)


def test_create_pending_object_factory_invalid_raises(task):
    rdi = MagicMock()
    with pytest.raises(ValueError, match="Unhandled sheet label"):
        task._create_pending_object_factory("invalid_sheet", rdi)


# --- _extract_household_id_from_row ---


def test_extract_household_id_from_row_none_idx_returns_none(task):
    row = _make_header_cells(["some_value"])
    obj_to_create = MagicMock()
    result = task._extract_household_id_from_row(row, None, "households", obj_to_create)
    assert result is None


def test_extract_household_id_from_row_string_value(task):
    cell = MagicMock()
    cell.value = "HH-ABC"
    row = (cell,)
    obj_to_create = MagicMock()
    result = task._extract_household_id_from_row(row, 0, "households", obj_to_create)
    assert result == "HH-ABC"


def test_extract_household_id_from_row_float_to_int(task):
    cell = MagicMock()
    cell.value = 1.0
    row = (cell,)
    obj_to_create = MagicMock()
    result = task._extract_household_id_from_row(row, 0, "households", obj_to_create)
    assert result == "1"


def test_extract_household_id_from_row_individuals_sets_household(task):
    mock_household = MagicMock()
    task.households = {"1": mock_household}
    cell = MagicMock()
    cell.value = 1.0
    row = (cell,)
    obj_to_create = MagicMock()
    result = task._extract_household_id_from_row(row, 0, "individuals", obj_to_create)
    assert result == "1"
    assert obj_to_create.household == mock_household


# --- _handle_head_of_household_relationship ---


def test_handle_head_of_household_sets_head(task):
    mock_household = MagicMock()
    task.households = {"1": mock_household}
    rel_cell = MagicMock()
    rel_cell.value = HEAD
    row = (MagicMock(), rel_cell)
    obj_to_create = MagicMock()
    households_to_update = []
    task._handle_head_of_household_relationship(row, 1, "1", obj_to_create, households_to_update)
    assert mock_household.head_of_household == obj_to_create
    assert mock_household in households_to_update


def test_handle_head_of_household_no_rel_col_noop(task):
    mock_household = MagicMock()
    task.households = {"1": mock_household}
    row = (MagicMock(),)
    obj_to_create = MagicMock()
    households_to_update = []
    task._handle_head_of_household_relationship(row, None, "1", obj_to_create, households_to_update)
    assert households_to_update == []


def test_handle_head_of_household_non_head_noop(task):
    mock_household = MagicMock()
    task.households = {"1": mock_household}
    rel_cell = MagicMock()
    rel_cell.value = "WIFE"
    row = (MagicMock(), rel_cell)
    obj_to_create = MagicMock()
    households_to_update = []
    task._handle_head_of_household_relationship(row, 1, "1", obj_to_create, households_to_update)
    assert households_to_update == []


# --- _process_lookup_field ---


def test_process_lookup_field_sets_value(task):
    obj_to_create = MagicMock()
    obj_to_create.some_lookup = "old"
    combined_fields = {"some_header": {"lookup": "some_lookup"}}
    task.COMBINED_FIELDS["some_header"] = {"type": "STRING"}
    result = task._process_lookup_field("some_header", "raw", obj_to_create, combined_fields)
    assert result is True
    assert obj_to_create.some_lookup == "raw"


def test_process_lookup_field_household_id_returns_false(task):
    obj_to_create = MagicMock()
    combined_fields = {"household_id": {"lookup": "household"}}
    result = task._process_lookup_field("household_id", "val", obj_to_create, combined_fields)
    assert result is False


def test_process_lookup_field_empty_value_returns_true(task):
    obj_to_create = MagicMock()
    obj_to_create.some_lookup = "old"
    combined_fields = {"some_header": {"lookup": "some_lookup"}}
    result = task._process_lookup_field("some_header", None, obj_to_create, combined_fields)
    assert result is True
    # value should not have been changed since cast returned None
    assert obj_to_create.some_lookup == "old"


# --- _process_flex_field ---


def test_process_flex_field_not_in_flex_fields(task):
    task.FLEX_FIELDS = {"individuals": {}}
    obj_to_create = MagicMock()
    obj_to_create.flex_fields = {}
    result = task._process_flex_field("unknown_header", "val", MagicMock(), obj_to_create, "individuals", {}, {})
    assert result is False


def test_process_flex_field_simple_type(task):
    task.FLEX_FIELDS = {"individuals": {"flex_header": {"type": "STRING"}}}
    task.COMBINED_FIELDS["flex_header"] = {"type": "STRING"}
    obj_to_create = MagicMock()
    obj_to_create.flex_fields = {}
    result = task._process_flex_field("flex_header", "raw", MagicMock(), obj_to_create, "individuals", {}, {})
    assert result is True
    assert obj_to_create.flex_fields["flex_header"] == "raw"


def test_process_flex_field_complex_type_calls_handler(task):
    task.FLEX_FIELDS = {"individuals": {"flex_header": {"type": "IMAGE"}}}
    task.COMBINED_FIELDS["flex_header"] = {"type": "STRING"}
    handler = MagicMock(return_value="image_path")
    complex_types = {"IMAGE": handler}
    obj_to_create = MagicMock()
    obj_to_create.flex_fields = {}
    cell = MagicMock()
    current_field = {"required": True}
    result = task._process_flex_field(
        "flex_header", "raw", cell, obj_to_create, "individuals", current_field, complex_types
    )
    assert result is True
    handler.assert_called_once_with(
        value="raw", cell=cell, header="flex_header", is_flex_field=True, is_field_required=True
    )
    assert obj_to_create.flex_fields["flex_header"] == "image_path"


def test_process_flex_field_none_value_not_set(task):
    task.FLEX_FIELDS = {"individuals": {"flex_header": {"type": "STRING"}}}
    obj_to_create = MagicMock()
    obj_to_create.flex_fields = {}
    result = task._process_flex_field("flex_header", None, MagicMock(), obj_to_create, "individuals", {}, {})
    assert result is True
    assert "flex_header" not in obj_to_create.flex_fields


# --- _build_complex_fields_config ---


def test_build_complex_fields_config_returns_two_dicts(task):
    complex_fields, complex_types = task._build_complex_fields_config()
    assert isinstance(complex_fields, dict)
    assert isinstance(complex_types, dict)


def test_build_complex_fields_config_has_expected_individual_keys(task):
    complex_fields, _ = task._build_complex_fields_config()
    individuals_keys = complex_fields["individuals"]
    assert "photo_i_c" in individuals_keys
    assert "primary_collector_id" in individuals_keys
    assert "alternate_collector_id" in individuals_keys
    assert "unhcr_id_no_i_c" in individuals_keys
    assert "scope_id_no_i_c" in individuals_keys


def test_build_complex_fields_config_complex_types_has_expected_keys(task):
    _, complex_types = task._build_complex_fields_config()
    assert "GEOPOINT" in complex_types
    assert "IMAGE" in complex_types
    assert "DECIMAL" in complex_types
    assert "BOOL" in complex_types


def test_build_complex_fields_config_with_document_types(task):
    from extras.test_utils.factories import DocumentTypeFactory

    DocumentTypeFactory(key="birth_certificate")
    complex_fields, _ = task._build_complex_fields_config()
    individuals_keys = complex_fields["individuals"]
    assert "birth_certificate_i_c" in individuals_keys
    assert "birth_certificate_no_i_c" in individuals_keys
    assert "birth_certificate_photo_i_c" in individuals_keys
    assert "birth_certificate_issuer_i_c" in individuals_keys


def test_process_regular_field_country_header(task):
    from extras.test_utils.factories import CountryFactory

    country = CountryFactory(iso_code3="AFG", name="Afghanistan")
    obj = MagicMock()
    obj.flex_fields = {}
    obj.country = None
    combined_fields = {"country_h_c": {"name": "country"}}
    task.COMBINED_FIELDS["country_h_c"] = {"type": "STRING"}
    cell = MagicMock()
    cell.value = "AFG"
    result = task._process_regular_field("country_h_c", "AFG", cell, obj, combined_fields)
    assert result is True
    assert obj.country == country


def test_process_regular_field_admin_header(task):
    from extras.test_utils.factories import AreaFactory, AreaTypeFactory, CountryFactory

    country = CountryFactory(iso_code3="AFG", name="Afghanistan")
    area_type = AreaTypeFactory(country=country, area_level=1)
    area = AreaFactory(area_type=area_type, p_code="AF01", name="Kabul")
    obj = MagicMock()
    obj.admin1 = None
    combined_fields = {"admin1_h_c": {"name": "admin1"}}
    task.COMBINED_FIELDS["admin1_h_c"] = {"type": "STRING"}
    cell = MagicMock()
    cell.value = "AF01"
    result = task._process_regular_field("admin1_h_c", "AF01", cell, obj, combined_fields)
    assert result is True
    assert obj.admin1 == area


def test_process_regular_field_org_enumerator(task):
    obj = MagicMock()
    obj.flex_fields = {}
    obj.org_enumerator = None
    combined_fields = {"org_enumerator_h_c": {"name": "org_enumerator"}}
    task.COMBINED_FIELDS["org_enumerator_h_c"] = {"type": "STRING"}
    cell = MagicMock()
    cell.value = "ENUM-001"
    result = task._process_regular_field("org_enumerator_h_c", "ENUM-001", cell, obj, combined_fields)
    assert result is True
    assert obj.flex_fields["enumerator_id"] == "ENUM-001"


def test_process_complex_field_households_sheet(task):
    handler = MagicMock(return_value="processed")
    obj = MagicMock()
    cell = MagicMock()
    cell.row = 5
    complex_fields = {"households": {"hh_field": handler}}
    combined_fields = {"hh_field": {"name": "hh_attr"}}
    result = task._process_complex_field(
        "hh_field", "raw", cell, obj, complex_fields, "households", {"required": True}, combined_fields
    )
    assert result is True
    handler.assert_called_once_with(
        value="raw",
        cell=cell,
        header="hh_field",
        row_num=5,
        individual=None,
        household=obj,
        is_field_required=True,
    )
    assert obj.hh_attr == "processed"


def test_handle_head_of_household_household_not_found(task):
    task.households = {}
    rel_cell = MagicMock()
    rel_cell.value = HEAD
    row = (MagicMock(), rel_cell)
    obj = MagicMock()
    households_to_update = []
    task._handle_head_of_household_relationship(row, 1, "missing_id", obj, households_to_update)
    assert households_to_update == []


# --- _finalize_row_object ---


def test_finalize_row_object_households(task, rdi):
    task.households = {}
    obj = MagicMock()
    row = (MagicMock(row=3),)
    task._finalize_row_object(obj, row, (), "households", "HH-1", rdi)
    assert task.households["HH-1"] == obj
    assert obj.business_area == rdi.business_area


def test_finalize_row_object_individuals_no_household_id(task, rdi):
    from hope.apps.household.const import NON_BENEFICIARY

    obj = MagicMock(birth_date="2000-01-01", flex_fields={})
    row = (MagicMock(row=5),)
    task.individuals = []
    with (
        patch.object(task, "_validate_birth_date", return_value=obj),
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.calculate_age_at_registration", return_value=25),
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.populate_pdu_with_null_values"),
        patch.object(task, "handle_pdu_fields"),
    ):
        task._finalize_row_object(obj, row, (), "individuals", None, rdi)
    assert obj.relationship == NON_BENEFICIARY
    assert obj in task.individuals


def test_finalize_row_object_individuals_with_household_id(task, rdi):
    obj = MagicMock(birth_date="2000-01-01", flex_fields={})
    row = (MagicMock(row=5),)
    task.individuals = []
    with (
        patch.object(task, "_validate_birth_date", return_value=obj),
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.calculate_age_at_registration", return_value=25),
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.populate_pdu_with_null_values"),
        patch.object(task, "handle_pdu_fields"),
    ):
        task._finalize_row_object(obj, row, (), "individuals", "HH-1", rdi)
    # relationship should NOT be set to NON_BENEFICIARY when household_id is provided
    assert obj in task.individuals


# --- _bulk_save_and_finalize ---


def test_bulk_save_and_finalize_households(task, rdi):
    hh_mock = MagicMock()
    task.households = {"HH-1": hh_mock}
    with patch("hope.apps.registration_data.tasks.rdi_xlsx_create.PendingHousehold") as mock_ph:
        task._bulk_save_and_finalize("households", [], rdi)
    mock_ph.all_objects.bulk_create.assert_called_once()
    args = mock_ph.all_objects.bulk_create.call_args[0][0]
    assert list(args) == [hh_mock]


def test_bulk_save_and_finalize_individuals(task, rdi):
    task.individuals = [MagicMock()]
    with (
        patch.object(task, "execute_individuals_additional_steps"),
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.PendingIndividual") as mock_pi,
        patch("hope.apps.registration_data.tasks.rdi_xlsx_create.PendingHousehold") as mock_ph,
        patch.object(task, "_create_documents"),
        patch.object(task, "_create_identities"),
        patch.object(task, "_create_collectors"),
        patch.object(task, "_create_accounts"),
    ):
        rdi.bulk_update_household_size = MagicMock()
        households_to_update = [MagicMock()]
        task._bulk_save_and_finalize("individuals", households_to_update, rdi)
    mock_pi.all_objects.bulk_create.assert_called_once_with(task.individuals)
    mock_ph.all_objects.bulk_update.assert_called_once_with(households_to_update, ["head_of_household"], 1000)
    rdi.bulk_update_household_size.assert_called_once()
