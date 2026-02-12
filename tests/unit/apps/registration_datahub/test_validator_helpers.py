from collections import defaultdict
from unittest.mock import MagicMock

from hope.apps.registration_datahub.validators import (
    KoboProjectImportDataInstanceValidator,
    UploadXLSXInstanceValidator,
)

# --- _find_header_column_indices ---


def _make_header_cells(values):
    """Create a tuple of MagicMock cells with given .value attributes."""
    cells = []
    for val in values:
        cell = MagicMock()
        cell.value = val
        cells.append(cell)
    return tuple(cells)


def test_find_header_column_indices_both_present():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    first_row = _make_header_cells(["full_name_i_c", "household_id", "relationship_i_c", "age"])
    result = UploadXLSXInstanceValidator._find_header_column_indices(validator, first_row)
    assert result == (1, 2)


def test_find_header_column_indices_only_household_id():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    first_row = _make_header_cells(["household_id", "full_name_i_c", "age"])
    result = UploadXLSXInstanceValidator._find_header_column_indices(validator, first_row)
    assert result == (0, None)


def test_find_header_column_indices_only_relationship():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    first_row = _make_header_cells(["full_name_i_c", "relationship_i_c", "age"])
    result = UploadXLSXInstanceValidator._find_header_column_indices(validator, first_row)
    assert result == (None, 1)


def test_find_header_column_indices_neither_present():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    first_row = _make_header_cells(["full_name_i_c", "age", "gender"])
    result = UploadXLSXInstanceValidator._find_header_column_indices(validator, first_row)
    assert result == (None, None)


def test_find_header_column_indices_empty_row():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    first_row = _make_header_cells([])
    result = UploadXLSXInstanceValidator._find_header_column_indices(validator, first_row)
    assert result == (None, None)


# --- _init_doc_identity_dicts ---


def test_init_doc_identity_dicts_returns_two_dicts():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    identities, documents = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    assert isinstance(identities, dict)
    assert isinstance(documents, dict)


def test_init_doc_identity_dicts_identities_keys():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    identities, _ = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    assert "unhcr_id_no_i_c" in identities
    assert "scope_id_no_i_c" in identities
    assert identities["unhcr_id_no_i_c"]["partner"] == "UNHCR"
    assert identities["scope_id_no_i_c"]["partner"] == "WFP"


def test_init_doc_identity_dicts_identities_have_empty_lists():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    identities, _ = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    for value in identities.values():
        assert value["validation_data"] == []
        assert value["numbers"] == []
        assert value["issuing_countries"] == []


def test_init_doc_identity_dicts_documents_keys():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    _, documents = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    expected_doc_keys = {
        "birth_certificate_no_i_c",
        "drivers_license_no_i_c",
        "electoral_card_no_i_c",
        "national_id_no_i_c",
        "national_passport_no_i_c",
        "tax_id_no_i_c",
        "other_id_type_i_c",
        "other_id_no_i_c",
    }
    assert set(documents.keys()) == expected_doc_keys


def test_init_doc_identity_dicts_documents_types():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    _, documents = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    assert documents["birth_certificate_no_i_c"]["type"] == "BIRTH_CERTIFICATE"
    assert documents["national_passport_no_i_c"]["type"] == "NATIONAL_PASSPORT"
    assert documents["other_id_type_i_c"]["type"] == "OTHER"


def test_init_doc_identity_dicts_other_id_type_has_names_list():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    _, documents = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    assert "names" in documents["other_id_type_i_c"]
    assert documents["other_id_type_i_c"]["names"] == []


def test_init_doc_identity_dicts_other_id_no_is_empty():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    _, documents = UploadXLSXInstanceValidator._init_doc_identity_dicts(validator)
    assert documents["other_id_no_i_c"] == {}


# --- _validate_admin_column ---


def test_validate_admin_column_non_admin_header_returns_none():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "full_name_i_c", "some_value", 3, [])
    assert result is None


def test_validate_admin_column_admin1_with_value_appends_and_returns_none():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    admin_tuples = []
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "admin1_h_c", "AF01", 3, admin_tuples)
    assert result is None
    assert (3, "admin1_h_c", "AF01") in admin_tuples


def test_validate_admin_column_admin2_with_value_appends_and_returns_none():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    admin_tuples = []
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "admin2_h_c", "AF0101", 5, admin_tuples)
    assert result is None
    assert (5, "admin2_h_c", "AF0101") in admin_tuples


def test_validate_admin_column_admin1_empty_returns_error():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "admin1_h_c", None, 3, [])
    assert result is not None
    assert result["row_number"] == 3
    assert result["header"] == "admin1_h_c"
    assert "cannot be null" in result["message"]


def test_validate_admin_column_admin2_empty_returns_error():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "admin2_h_c", "", 7, [])
    assert result is not None
    assert result["row_number"] == 7
    assert result["header"] == "admin2_h_c"


def test_validate_admin_column_admin3_empty_returns_none():
    """admin3 is not required, so empty value should not produce an error."""
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "admin3_h_c", None, 3, [])
    assert result is None


def test_validate_admin_column_pp_admin1_empty_returns_error():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "pp_admin1_i_c", None, 4, [])
    assert result is not None
    assert result["header"] == "pp_admin1_i_c"


def test_validate_admin_column_pp_admin2_empty_returns_error():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "pp_admin2_i_c", "", 6, [])
    assert result is not None
    assert result["header"] == "pp_admin2_i_c"


def test_validate_admin_column_pp_admin3_empty_returns_none():
    """pp_admin3_i_c is also not required."""
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "pp_admin3_i_c", None, 3, [])
    assert result is None


def test_validate_admin_column_pp_admin1_with_value_appends():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    admin_tuples = []
    result = UploadXLSXInstanceValidator._validate_admin_column(validator, "pp_admin1_i_c", "CODE1", 2, admin_tuples)
    assert result is None
    assert (2, "pp_admin1_i_c", "CODE1") in admin_tuples


# --- _validate_head_of_household (on UploadXLSXInstanceValidator) ---


def test_validate_head_of_household_all_valid():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    validator.head_of_household_count = defaultdict(int, {"HH1": 1, "HH2": 1})
    result = UploadXLSXInstanceValidator._validate_head_of_household(validator)
    assert result == []


def test_validate_head_of_household_missing_head():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    validator.head_of_household_count = defaultdict(int, {"HH1": 0})
    result = UploadXLSXInstanceValidator._validate_head_of_household(validator)
    assert len(result) == 1
    assert "has to have a head of household" in result[0]["message"]
    assert result[0]["header"] == "relationship_i_c"
    assert result[0]["row_number"] == 0


def test_validate_head_of_household_multiple_heads():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    validator.head_of_household_count = defaultdict(int, {"HH1": 3})
    result = UploadXLSXInstanceValidator._validate_head_of_household(validator)
    assert len(result) == 1
    assert "multiple head of households" in result[0]["message"]


def test_validate_head_of_household_mixed_errors():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    validator.head_of_household_count = defaultdict(int, {"HH1": 0, "HH2": 2, "HH3": 1})
    result = UploadXLSXInstanceValidator._validate_head_of_household(validator)
    assert len(result) == 2
    messages = [r["message"] for r in result]
    assert any("has to have a head of household" in m for m in messages)
    assert any("multiple head of households" in m for m in messages)


def test_validate_head_of_household_empty_dict():
    validator = MagicMock(spec=UploadXLSXInstanceValidator)
    validator.head_of_household_count = defaultdict(int)
    result = UploadXLSXInstanceValidator._validate_head_of_household(validator)
    assert result == []


# --- _validate_household_roles (on KoboProjectImportDataInstanceValidator) ---


def test_validate_household_roles_all_valid():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 1, 1)
    assert result == []


def test_validate_household_roles_no_head():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 0, 1, 0)
    assert len(result) == 1
    assert result[0]["header"] == "relationship_i_c"
    assert "has to have a head of household" in result[0]["message"]


def test_validate_household_roles_multiple_heads():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 2, 1, 0)
    assert len(result) == 1
    assert "Only one person can be a head" in result[0]["message"]


def test_validate_household_roles_no_primary_collector():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 0, 0)
    assert len(result) == 1
    assert result[0]["header"] == "role_i_c"
    assert "must have a primary collector" in result[0]["message"]


def test_validate_household_roles_multiple_primary_collectors():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 2, 0)
    assert len(result) == 1
    assert "Only one person can be a primary collector" in result[0]["message"]


def test_validate_household_roles_multiple_alternate_collectors():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 1, 2)
    assert len(result) == 1
    assert "Only one person can be a alternate collector" in result[0]["message"]


def test_validate_household_roles_all_errors():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 0, 0, 2)
    assert len(result) == 3
    headers = [e["header"] for e in result]
    assert "relationship_i_c" in headers
    assert "role_i_c" in headers


def test_validate_household_roles_zero_alternate_is_ok():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 1, 0)
    assert result == []


def test_validate_household_roles_exactly_one_of_each():
    validator = MagicMock(spec=KoboProjectImportDataInstanceValidator)
    result = KoboProjectImportDataInstanceValidator._validate_household_roles(validator, 1, 1, 1)
    assert result == []
