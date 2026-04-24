from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
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
    PendingHouseholdFactory,
    ProgramFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
)
from hope.models import (
    Area,
    BusinessArea,
    Country,
    Document,
    DocumentType,
    Facility,
    Household,
    Individual,
    PendingHousehold,
    Program,
)
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


# --- can_be_erase ---


@pytest.fixture
def erased_household(business_area: BusinessArea, program: Program) -> Household:
    now = timezone.now()
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        is_removed=True,
        withdrawn=True,
        removed_date=now,
        withdrawn_date=now,
    )


def test_can_be_erase_raises_type_error_when_dates_are_none(business_area: BusinessArea, program: Program) -> None:
    hh = HouseholdFactory(
        business_area=business_area,
        program=program,
        is_removed=True,
        withdrawn=True,
        removed_date=None,
        withdrawn_date=None,
    )

    with pytest.raises(TypeError):
        hh.can_be_erase()


def test_can_be_erase_returns_true_when_all_conditions_met(erased_household: Household) -> None:
    assert erased_household.can_be_erase() is True


def test_can_be_erase_returns_false_when_dates_too_old(business_area: BusinessArea, program: Program) -> None:
    old_date = timezone.now() - timedelta(days=2)
    hh = HouseholdFactory(
        business_area=business_area,
        program=program,
        is_removed=True,
        withdrawn=True,
        removed_date=old_date,
        withdrawn_date=old_date,
    )

    assert hh.can_be_erase() is False


# --- PendingHousehold setters ---


@pytest.fixture
def pending_household() -> PendingHousehold:
    return PendingHouseholdFactory()


def test_pending_household_individuals_getter(pending_household: PendingHousehold) -> None:
    result = pending_household.individuals

    assert result is not None


def test_pending_household_individuals_and_roles_getter(pending_household: PendingHousehold) -> None:
    result = pending_household.individuals_and_roles

    assert result is not None


def test_pending_household_pending_representatives(pending_household: PendingHousehold) -> None:
    result = pending_household.pending_representatives

    assert result is not None


# --- Facility ---


def test_facility_str(business_area: BusinessArea, area_hierarchy: tuple[Area, Area, Area, Area]) -> None:
    area1 = area_hierarchy[0]
    facility = Facility.objects.create(name="test facility", business_area=business_area, admin_area=area1)

    assert str(facility) == "TEST FACILITY"


def test_individual_erase(business_area: BusinessArea) -> None:
    individual = IndividualFactory(
        business_area=business_area,
        full_name="FullName",
        given_name="G_Name",
        middle_name="M_Name",
        family_name="F_Name",
        full_name_latin="LatinFull",
        given_name_latin="LatinGiven",
        middle_name_latin="MLatin",
        family_name_latin="Family latin",
    )
    individual.erase()
    assert individual.full_name == "GDPR REMOVED"
    assert individual.given_name == "GDPR REMOVED"
    assert individual.middle_name == "GDPR REMOVED"
    assert individual.family_name == "GDPR REMOVED"
    assert individual.full_name_latin == "GDPR REMOVED"
    assert individual.given_name_latin == "GDPR REMOVED"
    assert individual.middle_name_latin == "GDPR REMOVED"
    assert individual.family_name_latin == "GDPR REMOVED"


def test_individual_set_latin_names(business_area: BusinessArea) -> None:
    individual = IndividualFactory(
        business_area=business_area, full_name="甜的 針 昏迷", given_name="甜的", middle_name="針", family_name="昏迷"
    )
    individual.set_names_latin()
    assert individual.full_name_latin == "Tian De Zhen Hun Mi"
    assert individual.given_name_latin == "Tian De"
    assert individual.middle_name_latin == "Zhen"
    assert individual.family_name_latin == "Hun Mi"


def test_individual_set_latin_names_full_name(business_area: BusinessArea) -> None:
    individual = IndividualFactory(
        business_area=business_area, given_name="عبد الملك", middle_name="جولر", family_name="الفرامل"
    )
    # calculate based on first, middle, last names
    individual.full_name = None
    individual.set_names_latin()
    assert individual.full_name_latin == "Bd Lmlk Jwlr Lfrml"
    assert individual.given_name_latin == "Bd Lmlk"
    assert individual.middle_name_latin == "Jwlr"
    assert individual.family_name_latin == "Lfrml"

    # provide full name latin
    individual_2 = IndividualFactory(
        business_area=business_area,
        full_name="Provided Latin Name",
        given_name="عبد الملك",
        middle_name="جولر",
        family_name="الفرامل",
    )
    individual_2.set_names_latin()
    assert individual_2.full_name_latin == "Provided Latin Name"


def test_individual_set_latin_names_validation_error(business_area: BusinessArea) -> None:
    individual = IndividualFactory(business_area=business_area, full_name="2222222")
    with pytest.raises(ValidationError) as error:
        individual.set_names_latin()

    assert individual.full_name_latin is None
    assert "Only ASCII letters, spaces, hyphens, and apostrophes are allowed." in str(error.value)
