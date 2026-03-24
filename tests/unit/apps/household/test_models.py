from django.db import IntegrityError
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
)
from hope.models import Area, BusinessArea, Country, Document, DocumentType, Household, Individual, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


# --- Household ---


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def area_hierarchy() -> tuple[Area, Area, Area, Area]:
    area_type_1 = AreaTypeFactory(name="State1", area_level=1)
    area_type_2 = AreaTypeFactory(name="State2", area_level=2)
    area_type_3 = AreaTypeFactory(name="State3", area_level=3)
    area_type_4 = AreaTypeFactory(name="State4", area_level=4)
    area1 = AreaFactory(name="City Test1", area_type=area_type_1, p_code="area1")
    area2 = AreaFactory(name="City Test2", area_type=area_type_2, p_code="area2", parent=area1)
    area3 = AreaFactory(name="City Test3", area_type=area_type_3, p_code="area3", parent=area2)
    area4 = AreaFactory(name="City Test4", area_type=area_type_4, p_code="area4", parent=area3)
    return area1, area2, area3, area4


@pytest.fixture
def household(business_area: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(business_area=business_area, program=program)


@pytest.fixture
def country() -> Country:
    return CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")


@pytest.fixture
def individual(business_area: BusinessArea, program: Program) -> Individual:
    return HouseholdFactory(business_area=business_area, program=program).head_of_household


def test_household_admin_areas_set(household, area_hierarchy) -> None:
    area1, area2, area3, area4 = area_hierarchy
    household.admin1 = area1
    household.save()

    household.set_admin_areas()
    household.refresh_from_db()

    assert household.admin_area == area1
    assert household.admin1 == area1
    assert household.admin2 is None
    assert household.admin3 is None
    assert household.admin4 is None

    household.set_admin_areas(area4)
    household.refresh_from_db()

    assert household.admin_area == area4
    assert household.admin1 == area1
    assert household.admin2 == area2
    assert household.admin3 == area3
    assert household.admin4 == area4

    household.set_admin_areas(area3)
    household.refresh_from_db()

    assert household.admin_area == area3
    assert household.admin1 == area1
    assert household.admin2 == area2
    assert household.admin3 == area3
    assert household.admin4 is None


def test_household_set_admin_area_based_on_lowest_admin(household, area_hierarchy) -> None:
    area1, area2, area3, area4 = area_hierarchy
    household.admin1 = None
    household.admin2 = None
    household.admin3 = None
    household.admin4 = area4

    household.set_admin_areas()
    household.refresh_from_db()

    assert household.admin_area == area4
    assert household.admin1 == area1
    assert household.admin2 == area2
    assert household.admin3 == area3
    assert household.admin4 == area4


def test_remove_household(business_area, program) -> None:
    household1 = HouseholdFactory(business_area=business_area, program=program, unicef_id="HH-9090")
    household2 = HouseholdFactory(business_area=business_area, program=program, unicef_id="HH-9191")

    household1.head_of_household = None
    household1.save()
    household1.delete()
    assert Household.all_objects.filter(unicef_id="HH-9090").first().is_removed is True

    household2.head_of_household = None
    household2.save()
    household2.delete(soft=False)
    assert Household.all_objects.filter(unicef_id="HH-9191").first() is None


def test_unique_unicef_id_per_program_constraint_household(program) -> None:
    HouseholdFactory(unicef_id="HH-123", program=program)
    HouseholdFactory(unicef_id="HH-000", program=program)
    with pytest.raises(IntegrityError):
        HouseholdFactory(unicef_id="HH-123", program=program)


def test_geopoint(household) -> None:
    household.geopoint = 1.2, 0.5  # type: ignore
    assert household.longitude == 1.2
    assert household.latitude == 0.5
    household.geopoint = None
    assert household.longitude is None
    assert household.latitude is None


# --- Document ---


def _make_document(
    individual: Individual,
    country: Country,
    program: Program,
    document_type: DocumentType,
    document_number: str,
    **kwargs,
) -> Document:
    return Document.objects.create(
        document_number=document_number,
        individual=individual,
        country=country,
        type=document_type,
        status=Document.STATUS_VALID,
        program=program,
        **kwargs,
    )


def test_raise_error_on_creating_duplicated_documents_with_the_same_number_not_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_OTHER],
        defaults={"label": "Other", "unique_for_individual": False},
    )
    _make_document(individual, country, program, document_type, "213123", rdi_merge_status=MergeStatusModel.MERGED)
    with pytest.raises(IntegrityError):
        _make_document(individual, country, program, document_type, "213123", rdi_merge_status=MergeStatusModel.MERGED)


def test_create_duplicated_documents_with_different_numbers_and_not_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_OTHER],
        defaults={"label": "Other", "unique_for_individual": False},
    )
    _make_document(individual, country, program, document_type, "213123", rdi_merge_status=MergeStatusModel.MERGED)
    _make_document(individual, country, program, document_type, "213124", rdi_merge_status=MergeStatusModel.MERGED)


def test_raise_error_on_creating_duplicated_documents_with_the_same_number_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        defaults={"label": "National Passport", "unique_for_individual": True},
    )
    _make_document(individual, country, program, document_type, "213123", rdi_merge_status=MergeStatusModel.MERGED)
    with pytest.raises(IntegrityError):
        _make_document(individual, country, program, document_type, "213123", rdi_merge_status=MergeStatusModel.MERGED)


def test_create_document_of_the_same_type_for_individual_not_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        defaults={"label": "National Passport", "unique_for_individual": False},
    )
    _make_document(individual, country, program, document_type, "213123")
    _make_document(individual, country, program, document_type, "11111")


def test_raise_error_on_creating_document_of_the_same_type_for_individual_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        defaults={"label": "National Passport", "unique_for_individual": True},
    )
    _make_document(individual, country, program, document_type, "213123")
    with pytest.raises(IntegrityError):
        _make_document(individual, country, program, document_type, "11111")


def test_raise_error_on_creating_duplicated_documents_with_different_numbers_and_unique_for_individual(
    individual, country, program
) -> None:
    document_type, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        defaults={"label": "National Passport", "unique_for_individual": True},
    )
    _make_document(individual, country, program, document_type, "123", rdi_merge_status=MergeStatusModel.MERGED)
    with pytest.raises(IntegrityError):
        _make_document(individual, country, program, document_type, "456", rdi_merge_status=MergeStatusModel.MERGED)


def test_create_duplicated_documents_with_different_numbers_and_types_and_unique_for_individual(
    individual, country, program
) -> None:
    doc_type_1, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        defaults={"label": "National Passport", "unique_for_individual": True},
    )
    doc_type_2, _ = DocumentType.objects.update_or_create(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        defaults={"label": "Tax Number Identification", "unique_for_individual": True},
    )
    _make_document(individual, country, program, doc_type_1, "213123", rdi_merge_status=MergeStatusModel.MERGED)
    _make_document(individual, country, program, doc_type_2, "213124", rdi_merge_status=MergeStatusModel.MERGED)


# --- Individual ---


def test_unique_unicef_id_per_program_constraint_individual(program) -> None:
    IndividualFactory(unicef_id="IND-123", program=program)
    IndividualFactory(unicef_id="IND-000", program=program)
    with pytest.raises(IntegrityError):
        IndividualFactory(unicef_id="IND-123", program=program)


def test_mark_as_distinct_raise_errors(program) -> None:
    ind = IndividualFactory(unicef_id="IND-333", program=program)
    doc_type = DocumentTypeFactory(key="registration_token")
    country = CountryFactory()
    DocumentFactory(
        status=Document.STATUS_VALID,
        program=program,
        type=doc_type,
        document_number="123456ABC",
        individual=ind,
        country=country,
    )
    doc_2 = DocumentFactory(
        status=Document.STATUS_INVALID,
        program=program,
        type=doc_type,
        document_number="aaa",
        individual=ind,
        country=country,
    )
    doc_2.document_number = "123456ABC"
    doc_2.save()

    with pytest.raises(Exception, match="IND-333: Valid Document already exists: 123456ABC."):
        ind.mark_as_distinct()
