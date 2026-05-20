from django.conf import settings
from django.core.exceptions import ValidationError
from openpyxl.utils.exceptions import InvalidFileException
import pytest

from hope.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hope.models import FlexibleAttribute, FlexibleAttributeChoice, FlexibleAttributeGroup


def _load_xls(name: str) -> None:
    task = FlexibleAttributeImporter()
    task.import_xls(f"{settings.TESTS_ROOT}/apps/core/test_files/{name}")


@pytest.fixture
def imported_flex_init(db):
    _load_xls("flex_init.xlsx")


@pytest.fixture
def imported_flex_init_valid_types(db):
    _load_xls("flex_init_valid_types.xlsx")


@pytest.fixture
def imported_and_updated(imported_flex_init):
    _load_xls("flex_updated.xlsx")


def test_flex_import_creates_expected_attribute_count(imported_flex_init):
    attrs_from_db = FlexibleAttribute.objects.all()

    assert len(attrs_from_db) == 45


def test_flex_import_creates_expected_group_count(imported_flex_init):
    groups_from_db = FlexibleAttributeGroup.objects.all()

    assert len(groups_from_db) == 10


def test_flex_import_creates_expected_repeated_groups_count(imported_flex_init):
    groups_from_db = FlexibleAttributeGroup.objects.filter(repeatable=True)

    assert len(groups_from_db) == 2


def test_flex_import_creates_expected_choice_count(imported_flex_init):
    choices_from_db = FlexibleAttributeChoice.objects.all()

    assert len(choices_from_db) == 441


@pytest.mark.parametrize(
    "group_name",
    [
        pytest.param("consent", id="consent"),
        pytest.param("household_questions", id="household_questions"),
        pytest.param("individual_questions", id="individual_questions"),
    ],
)
def test_flex_import_creates_root_group_without_parent(imported_flex_init, group_name):
    group = FlexibleAttributeGroup.objects.get(name=group_name)

    assert group.parent is None


@pytest.mark.parametrize(
    ("group_name", "expected_parent_name"),
    [
        pytest.param("header_hh_size", "household_questions", id="header_hh_size"),
        pytest.param("composition_female", "household_questions", id="composition_female"),
        pytest.param("composition_male", "household_questions", id="composition_male"),
        pytest.param("household_vulnerabilities", "household_questions", id="household_vulnerabilities"),
        pytest.param("contact_details_i_c", "individual_questions", id="contact_details_i_c"),
        pytest.param("id_questions", "individual_questions", id="id_questions"),
        pytest.param("vulnerability_questions", "individual_questions", id="vulnerability_questions"),
    ],
)
def test_flex_import_creates_child_group_with_correct_parent(imported_flex_init, group_name, expected_parent_name):
    group = FlexibleAttributeGroup.objects.get(name=group_name)

    assert group.parent.name == expected_parent_name


@pytest.mark.parametrize(
    ("attr_name", "expected_label", "expected_associated_with"),
    [
        pytest.param(
            "unaccompanied_child_h_f",
            "Does your family host an unaccompanied child / fosterchild?",
            0,
            id="unaccompanied_child_h_f",
        ),
        pytest.param(
            "recent_illness_child_h_f",
            "Has any of your children been ill with cough and fever at any time in the last 2 weeks?",
            0,
            id="recent_illness_child_h_f",
        ),
        pytest.param(
            "difficulty_breathing_h_f",
            "If any child was sick, When he/she had an illness with a cough, did he/she breathe "
            "faster than usual with short, rapid breaths or have difficulty breathing?",
            0,
            id="difficulty_breathing_h_f",
        ),
        pytest.param(
            "treatment_h_f",
            "If above is Yes, did you seek advice or treatment for the illness from any source?",
            0,
            id="treatment_h_f",
        ),
        pytest.param(
            "school_enrolled_before_i_f",
            "If member is a child, does he/she ever been enrolled in school?",
            1,
            id="school_enrolled_before_i_f",
        ),
        pytest.param(
            "school_enrolled_i_f",
            "If member is a child, does he/she currently enrolled in school",
            1,
            id="school_enrolled_i_f",
        ),
    ],
)
def test_flex_import_assigns_yes_no_choices_to_attributes(
    imported_flex_init, attr_name, expected_label, expected_associated_with
):
    attrib = FlexibleAttribute.objects.get(name=attr_name)
    yes_choice = FlexibleAttributeChoice.objects.get(list_name="yes_no", name=1)
    no_choice = FlexibleAttributeChoice.objects.get(list_name="yes_no", name=0)

    assert attrib.label["English(EN)"] == expected_label
    assert attrib.associated_with == expected_associated_with
    assert yes_choice.flex_attributes.filter(id=attrib.id).exists()
    assert no_choice.flex_attributes.filter(id=attrib.id).exists()


@pytest.mark.parametrize(
    "group_name",
    [
        pytest.param("household_questions", id="household_questions"),
        pytest.param("header_hh_size", id="header_hh_size"),
        pytest.param("composition_female", id="composition_female"),
        pytest.param("composition_male", id="composition_male"),
        pytest.param("household_vulnerabilities", id="household_vulnerabilities"),
    ],
)
def test_flex_update_soft_deletes_groups(imported_and_updated, group_name):
    assert not FlexibleAttributeGroup.objects.filter(name=group_name).exists()
    assert FlexibleAttributeGroup.all_objects.filter(name=group_name, is_removed=True).exists()


def test_flex_update_modifies_group_label(imported_and_updated):
    consent_group = FlexibleAttributeGroup.objects.get(name="consent")

    assert consent_group.label["English(EN)"] == "Consent Edited"


def test_flex_update_removes_note_type_attribute(imported_and_updated):
    introduction_exists = FlexibleAttribute.objects.filter(type="note", name="introduction_h_f").exists()

    assert not introduction_exists


def test_flex_import_valid_types_creates_expected_counts(imported_flex_init_valid_types):
    groups_from_db = FlexibleAttributeGroup.objects.all()
    flex_attrs_from_db = FlexibleAttribute.objects.all()

    assert len(groups_from_db) == 1
    assert len(flex_attrs_from_db) == 1


def test_flex_import_valid_types_creates_attribute_with_correct_data(imported_flex_init_valid_types):
    result = FlexibleAttribute.objects.filter(
        type="STRING",
        name="introduction_h_f",
        label={
            "French(FR)": "",
            "English(EN)": "1) Greeting    "
            "2) Introduce yourself politely    "
            "3) I represent UNICEF    "
            "4) You have been selected to help us conduct "
            "a household needs assessment in your area.    "
            "5) This survey is voluntary and the information"
            " you provide will remain strictly "
            "confidential.    "
            "6) Participating in the evaluation does not "
            "mean that you are entitled to assistance. "
            "UNICEF will analyze the data for "
            "possible eligibility.    "
            "7) I will ask you a few questions "
            "and observe your installations in the house.",
        },
    ).exists()

    assert result


def test_flex_import_invalid_types_raises_validation_error_and_preserves_data(imported_flex_init_valid_types):
    with pytest.raises(ValidationError):
        _load_xls("flex_update_invalid_types.xlsx")

    group = FlexibleAttributeGroup.objects.all()
    attribs = FlexibleAttribute.objects.all()

    assert len(group) == 1
    assert len(attribs) == 1


def test_flex_import_missing_name_raises_validation_error(db):
    with pytest.raises(ValidationError, match="Name is required"):
        _load_xls("flex_field_missing_name.xlsx")

    assert FlexibleAttributeGroup.objects.count() == 0
    assert FlexibleAttribute.objects.count() == 0


def test_flex_import_missing_english_label_raises_validation_error(db):
    with pytest.raises(ValidationError, match="English label cannot be empty"):
        _load_xls("flex_field_missing_english_label.xlsx")

    assert FlexibleAttributeGroup.objects.count() == 0
    assert FlexibleAttribute.objects.count() == 0


def test_flex_import_invalid_file_raises_exception(db):
    with pytest.raises(InvalidFileException):
        _load_xls("erd arrows.jpg")


def test_flex_reimport_soft_deleted_objects_restores_relationship(imported_flex_init_valid_types):
    field = FlexibleAttribute.objects.get(name="introduction_h_f")
    group = FlexibleAttributeGroup.objects.get(name="consent")

    field.delete()
    group.delete()

    assert field.is_removed
    assert group.is_removed

    _load_xls("flex_init_valid_types.xlsx")

    assert field.group == group
