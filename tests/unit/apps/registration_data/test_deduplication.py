from datetime import date
from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import (
    DUPLICATE,
    FEMALE,
    HEAD,
    MALE,
    NEEDS_ADJUDICATION,
    SON_DAUGHTER,
    UNIQUE,
    WIFE_HUSBAND,
)
from hope.apps.household.documents import get_individual_doc
from hope.apps.registration_data.tasks.deduplicate import DeduplicateTask
from hope.apps.utils.elasticsearch_utils import populate_index, rebuild_search_index
from hope.apps.utils.querysets import evaluate_qs
from hope.models import (
    DUPLICATE_IN_BATCH,
    UNIQUE_IN_BATCH,
    Individual,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = [pytest.mark.usefixtures("django_elasticsearch_setup"), pytest.mark.elasticsearch]


@pytest.fixture
def batch_deduplication_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
        deduplication_duplicate_score=14.0,
        deduplication_possible_duplicate_score=11.0,
        deduplication_batch_duplicates_percentage=100,
        deduplication_batch_duplicates_allowed=10,
        deduplication_golden_record_duplicates_percentage=100,
        deduplication_golden_record_duplicates_allowed=10,
    )
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    importing_rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.IMPORTING,
    )
    merged_rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.MERGED,
    )

    pending_head = PendingIndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=importing_rdi,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=date(1955, 9, 4),
    )
    pending_household = PendingHouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=importing_rdi,
        head_of_household=pending_head,
        create_role=False,
    )
    pending_individuals = [
        pending_head,
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Tesa",
            full_name="Tesa Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="123-123-123",
            phone_no_alternative="",
            relationship=WIFE_HUSBAND,
            sex=FEMALE,
            birth_date=date(1957, 10, 10),
        ),
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Tescik",
            full_name="Tescik Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="123-123-123",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=date(1996, 12, 12),
        ),
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Tessta",
            full_name="Tessta Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="123-123-123",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=FEMALE,
            birth_date=date(1997, 7, 7),
        ),
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Test",
            full_name="Test Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="123-123-123",
            phone_no_alternative="",
            relationship=HEAD,
            sex=MALE,
            birth_date=date(1955, 9, 4),
        ),
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Test",
            full_name="Test Example",
            middle_name="",
            family_name="Example",
            phone_no="432-125-765",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=MALE,
            birth_date=date(1997, 8, 8),
        ),
        PendingIndividualFactory(
            household=pending_household,
            business_area=business_area,
            program=program,
            registration_data_import=importing_rdi,
            given_name="Tessta",
            full_name="Tessta Testowski",
            middle_name="",
            family_name="Testowski",
            phone_no="123-123-123",
            phone_no_alternative="",
            relationship=SON_DAUGHTER,
            sex=FEMALE,
            birth_date=date(1997, 7, 7),
        ),
    ]

    merged_head = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=merged_rdi,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=date(1955, 9, 4),
    )
    merged_household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=merged_rdi,
        head_of_household=merged_head,
        create_role=False,
    )
    IndividualFactory(
        household=merged_household,
        business_area=business_area,
        program=program,
        registration_data_import=merged_rdi,
        given_name="Test",
        full_name="Test Example",
        middle_name="",
        family_name="Example",
        phone_no="432-125-765",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=MALE,
        birth_date=date(1997, 8, 8),
    )
    IndividualFactory(
        household=merged_household,
        business_area=business_area,
        program=program,
        registration_data_import=merged_rdi,
        given_name="Tessta",
        full_name="Tessta Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=FEMALE,
        birth_date=date(1997, 7, 7),
    )
    IndividualFactory(
        household=merged_household,
        business_area=business_area,
        program=program,
        registration_data_import=merged_rdi,
        given_name="Tescik",
        full_name="Tescik Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="666-777-888",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=MALE,
        birth_date=date(1996, 12, 12),
    )

    rebuild_search_index()

    return {
        "business_area": business_area,
        "program": program,
        "registration_data_import": importing_rdi,
        "pending_individuals": pending_individuals,
    }


@pytest.fixture
def golden_record_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        deduplication_possible_duplicate_score=11.0,
        has_data_sharing_agreement=True,
    )
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    registration_data_import = RegistrationDataImportFactory(business_area=business_area, program=program)
    registration_data_import_second = RegistrationDataImportFactory(business_area=business_area, program=program)

    head_individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=date(1955, 9, 7),
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        head_of_household=head_individual,
        create_role=False,
    )
    IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        given_name="Tesa",
        full_name="Tesa Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="453-85-423",
        phone_no_alternative="",
        relationship=WIFE_HUSBAND,
        sex=FEMALE,
        birth_date=date(1955, 9, 5),
    )
    IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        given_name="Example",
        full_name="Example Example",
        middle_name="",
        family_name="Example",
        phone_no="934-25-25-121",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=MALE,
        birth_date=date(1985, 8, 12),
    )
    IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        given_name="Tessta",
        full_name="Tessta Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="363-224-112",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=FEMALE,
        birth_date=date(1989, 9, 10),
    )

    head_other = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import_second,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=date(1955, 9, 7),
    )
    other_household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import_second,
        head_of_household=head_other,
        create_role=False,
    )
    IndividualFactory(
        household=other_household,
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import_second,
        given_name="Tessta",
        full_name="Tessta Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="363-224-112",
        phone_no_alternative="",
        relationship=SON_DAUGHTER,
        sex=FEMALE,
        birth_date=date(1989, 9, 10),
    )

    rebuild_search_index()

    return {
        "business_area": business_area,
        "program": program,
        "registration_data_import": registration_data_import,
    }


def test_batch_deduplication(
    batch_deduplication_context: dict[str, Any],
    django_assert_num_queries: Any,
) -> None:
    business_area = batch_deduplication_context["business_area"]
    program = batch_deduplication_context["program"]
    registration_data_import = batch_deduplication_context["registration_data_import"]

    task = DeduplicateTask(business_area.slug, program.id)

    with django_assert_num_queries(22):
        task.deduplicate_pending_individuals(registration_data_import)

    duplicate_in_batch = PendingIndividual.objects.order_by("full_name").filter(
        deduplication_batch_status=DUPLICATE_IN_BATCH
    )
    unique_in_batch = PendingIndividual.objects.order_by("full_name").filter(deduplication_batch_status=UNIQUE_IN_BATCH)

    assert duplicate_in_batch.count() == 4
    assert unique_in_batch.count() == 3

    expected_duplicates = (
        "Tessta Testowski",
        "Tessta Testowski",
        "Test Testowski",
        "Test Testowski",
    )
    expected_uniques = (
        "Tesa Testowski",
        "Tescik Testowski",
        "Test Example",
    )
    assert tuple(duplicate_in_batch.values_list("full_name", flat=True)) == expected_duplicates
    assert tuple(unique_in_batch.values_list("full_name", flat=True)) == expected_uniques

    duplicate_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
        deduplication_golden_record_status=DUPLICATE
    )
    needs_adjudication_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
        deduplication_golden_record_status=NEEDS_ADJUDICATION
    )
    unique_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
        deduplication_golden_record_status=UNIQUE
    )

    assert duplicate_in_golden_record.count() == 5
    assert unique_in_golden_record.count() == 1
    assert needs_adjudication_in_golden_record.count() == 1

    expected_duplicates_gr = (
        "Tessta Testowski",
        "Tessta Testowski",
        "Test Example",
        "Test Testowski",
        "Test Testowski",
    )
    expected_uniques_gr = ("Tesa Testowski",)

    assert tuple(duplicate_in_golden_record.values_list("full_name", flat=True)) == expected_duplicates_gr
    assert tuple(unique_in_golden_record.values_list("full_name", flat=True)) == expected_uniques_gr


def test_golden_record_deduplication(
    golden_record_context: dict[str, Any],
    django_assert_num_queries: Any,
) -> None:
    business_area = golden_record_context["business_area"]
    program = golden_record_context["program"]
    registration_data_import = golden_record_context["registration_data_import"]

    task = DeduplicateTask(business_area.slug, program.id)
    individuals = evaluate_qs(
        Individual.objects.filter(registration_data_import=registration_data_import).select_for_update().order_by("pk")
    )
    populate_index(individuals, get_individual_doc(business_area.slug))

    with django_assert_num_queries(4):
        task.deduplicate_individuals_against_population(individuals)

    needs_adjudication = Individual.objects.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
    duplicate = Individual.objects.filter(deduplication_golden_record_status=DUPLICATE)

    assert needs_adjudication.count() == 0
    assert duplicate.count() == 4


def test_deduplicate_individuals_from_other_source(
    golden_record_context: dict[str, Any],
    django_assert_num_queries: Any,
) -> None:
    business_area = golden_record_context["business_area"]
    program = golden_record_context["program"]
    registration_data_import = golden_record_context["registration_data_import"]

    task = DeduplicateTask(business_area.slug, program.id)
    individuals = evaluate_qs(
        Individual.objects.filter(registration_data_import=registration_data_import).select_for_update().order_by("pk")
    )
    populate_index(individuals, get_individual_doc(business_area.slug))

    with django_assert_num_queries(4):
        task.deduplicate_individuals_from_other_source(individuals)

    needs_adjudication = Individual.objects.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
    duplicate = Individual.objects.filter(deduplication_golden_record_status=DUPLICATE)

    assert needs_adjudication.count() == 0
    assert duplicate.count() == 2
