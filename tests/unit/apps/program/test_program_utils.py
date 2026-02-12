"""Tests for program utility functions."""

import hashlib
import json
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.db.utils import IntegrityError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.household.celery_tasks import enroll_households_to_program_task
from hope.apps.household.const import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hope.apps.program.utils import (
    _create_enrollment_rdi,
    _format_integrity_error,
    _prepare_and_save_household_copy,
    enroll_households_to_program,
    generate_rdi_unique_name,
)
from hope.models import (
    BusinessArea,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def program1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(name="Program 1", business_area=afghanistan)


@pytest.fixture
def program2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(name="Program 2", business_area=afghanistan)


@pytest.fixture
def household_original_already_enrolled(program1: Program) -> Household:
    return HouseholdFactory(
        program=program1,
        head_of_household=IndividualFactory(household=None, program=program1),
    )


@pytest.fixture
def household_already_enrolled(
    program2: Program,
    household_original_already_enrolled: Household,
) -> Household:
    individual_already_enrolled = IndividualFactory(household=None, program=program2)
    household = HouseholdFactory(
        program=program2,
        head_of_household=individual_already_enrolled,
        copied_from=household_original_already_enrolled,
        unicef_id=household_original_already_enrolled.unicef_id,
    )
    individual_already_enrolled.household = household
    individual_already_enrolled.save()
    return household


@pytest.fixture
def individual_hoh(program1: Program) -> Individual:
    return IndividualFactory(household=None, program=program1)


@pytest.fixture
def individual1(program1: Program) -> Individual:
    ind = IndividualFactory(household=None, program=program1)
    DocumentFactory(individual=ind)
    IndividualIdentityFactory(individual=ind)
    return ind


@pytest.fixture
def individual_2_original(program1: Program) -> Individual:
    return IndividualFactory(household=None, program=program1)


@pytest.fixture
def individual_2_already_enrolled(program2: Program, individual_2_original: Individual) -> Individual:
    individual = IndividualFactory(household=None, program=program2)
    individual.copied_from = individual_2_original
    individual.unicef_id = individual_2_original.unicef_id
    individual.save()
    DocumentFactory(individual=individual)
    IndividualIdentityFactory(individual=individual)
    return individual


@pytest.fixture
def household(
    program1: Program,
    individual_hoh: Individual,
    individual1: Individual,
    individual_2_original: Individual,
) -> Household:
    household = HouseholdFactory(
        program=program1,
        head_of_household=individual_hoh,
    )
    household.refresh_from_db()
    household.individuals.set([individual1, individual_2_original])

    individual_hoh.household = household
    individual_hoh.save()

    IndividualRoleInHouseholdFactory(
        individual=individual_2_original,
        household=household,
        role=ROLE_ALTERNATE,
    )
    primary_role = IndividualRoleInHousehold.objects.get(
        household=household,
        role=ROLE_PRIMARY,
    )
    primary_role.individual = individual1
    primary_role.save()

    return household


@pytest.fixture
def individual_hoh_e(program1: Program) -> Individual:
    return IndividualFactory(household=None, program=program1)


@pytest.fixture
def household_external(program1: Program, individual_hoh_e: Individual) -> Household:
    household = HouseholdFactory(
        program=program1,
        head_of_household=individual_hoh_e,
    )
    individual_hoh_e.household = household
    individual_hoh_e.save()
    return household


@pytest.fixture
def individual_external(program1: Program, household_external: Household) -> Individual:
    ind = IndividualFactory(household=None, program=program1)
    primary_role = IndividualRoleInHousehold.objects.get(
        household=household_external,
        role=ROLE_PRIMARY,
    )
    primary_role.individual = ind
    primary_role.save()
    return ind


@pytest.fixture
def enrollment_test_data(
    user: User,
    program1: Program,
    program2: Program,
    household_original_already_enrolled: Household,
    household_already_enrolled: Household,
    household: Household,
    individual1: Individual,
    individual_2_original: Individual,
    individual_2_already_enrolled: Individual,
    individual_hoh: Individual,
    household_external: Household,
    individual_external: Individual,
    individual_hoh_e: Individual,
) -> dict:
    return {
        "user": user,
        "program1": program1,
        "program2": program2,
        "household_original_already_enrolled": household_original_already_enrolled,
        "household_already_enrolled": household_already_enrolled,
        "household": household,
        "individual1": individual1,
        "individual_2_original": individual_2_original,
        "individual_2_already_enrolled": individual_2_already_enrolled,
        "individual_hoh": individual_hoh,
        "household_external": household_external,
        "individual_external": individual_external,
        "individual_hoh_e": individual_hoh_e,
    }


@pytest.mark.usefixtures("mock_elasticsearch")
def test_enroll_household_to_program_already_enrolled(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()

    enroll_households_to_program(
        Household.objects.filter(id=enrollment_test_data["household_already_enrolled"].id),
        enrollment_test_data["program2"],
        str(enrollment_test_data["user"].pk),
    )
    assert hh_count == Household.objects.count()
    assert ind_count == Individual.objects.count()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_enroll_original_household_to_program_representation_already_enrolled(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()

    enroll_households_to_program(
        Household.objects.filter(id=enrollment_test_data["household_original_already_enrolled"].id),
        enrollment_test_data["program2"],
        str(enrollment_test_data["user"].pk),
    )
    assert hh_count == Household.objects.count()
    assert ind_count == Individual.objects.count()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_enroll_household_to_program(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()
    document_count = Document.objects.count()
    identities_count = IndividualIdentity.objects.count()
    roles_count = IndividualRoleInHousehold.objects.count()
    original_household_id = enrollment_test_data["household"].id

    enroll_households_to_program(
        Household.objects.filter(id=enrollment_test_data["household"].id),
        enrollment_test_data["program2"],
        str(enrollment_test_data["user"].pk),
    )

    enrollment_test_data["individual_2_already_enrolled"].refresh_from_db()
    # 1 new hh enrolled to program2
    assert hh_count + 1 == Household.objects.count()
    # 2 new individuals enrolled to program2, individual1 and individual_hoh, individual2 was already in program 2
    assert ind_count + 2 == Individual.objects.count()
    # 1 new object related to individual1 enrolled to program2
    assert document_count + 1 == Document.objects.count()
    assert identities_count + 1 == IndividualIdentity.objects.count()
    assert roles_count + 2 == IndividualRoleInHousehold.objects.count()

    original_household = Household.objects.get(id=original_household_id)
    enrolled_household = original_household.copied_to.first()

    assert enrollment_test_data["individual_2_already_enrolled"].household == enrolled_household
    assert original_household.copied_to.count() == 1
    assert enrolled_household.program == enrollment_test_data["program2"]
    assert enrolled_household.unicef_id == original_household.unicef_id
    assert (
        enrolled_household.head_of_household
        == enrollment_test_data["individual_hoh"].copied_to.filter(program=enrollment_test_data["program2"]).first()
    )
    assert enrolled_household.individuals.count() == original_household.individuals.count() == 3
    assert enrolled_household.individuals.first().program == enrollment_test_data["program2"]

    assert IndividualRoleInHousehold.objects.filter(
        individual=enrollment_test_data["individual1"]
        .copied_to.filter(program=enrollment_test_data["program2"])
        .first(),
        household=enrolled_household,
        role=ROLE_PRIMARY,
    ).first()
    assert IndividualRoleInHousehold.objects.filter(
        individual=enrollment_test_data["individual_2_original"]
        .copied_to.filter(program=enrollment_test_data["program2"])
        .first(),
        household=enrolled_household,
        role=ROLE_ALTERNATE,
    ).first()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_enroll_household_with_external_collector(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()
    roles_count = IndividualRoleInHousehold.objects.count()

    enroll_households_to_program(
        Household.objects.filter(id=enrollment_test_data["household_external"].id),
        enrollment_test_data["program2"],
        str(enrollment_test_data["user"].pk),
    )
    hh = Household.objects.order_by("created_at").last()
    assert hh_count + 1 == Household.objects.count()
    # 2 new individuals enrolled - individual_external and individual_hoh
    assert ind_count + 2 == Individual.objects.count()
    assert roles_count + 1 == IndividualRoleInHousehold.objects.count()

    assert (
        hh.head_of_household
        == enrollment_test_data["individual_hoh_e"].copied_to.filter(program=enrollment_test_data["program2"]).first()
    )
    assert (
        enrollment_test_data["individual_external"].copied_to.filter(program=enrollment_test_data["program2"]).first()
        is not None
    )
    assert (
        IndividualRoleInHousehold.objects.filter(
            individual=enrollment_test_data["individual_external"]
            .copied_to.filter(program=enrollment_test_data["program2"])
            .first(),
            household=hh,
            role=ROLE_PRIMARY,
        ).first()
        is not None
    )


@pytest.mark.usefixtures("mock_elasticsearch")
def test_enroll_household_with_head_of_household_already_copied(enrollment_test_data: dict) -> None:
    head_of_household_already_enrolled_program1 = IndividualFactory(
        household=None, program=enrollment_test_data["program1"]
    )
    head_of_household_already_enrolled_program1.refresh_from_db()

    head_of_household_already_enrolled_program2 = IndividualFactory(
        household=None,
        program=enrollment_test_data["program2"],
        unicef_id=head_of_household_already_enrolled_program1.unicef_id,
    )

    household_already_with_head_already_enrolled = HouseholdFactory(
        program=enrollment_test_data["program1"],
        head_of_household=head_of_household_already_enrolled_program1,
        copied_from=None,
    )
    head_of_household_already_enrolled_program1.household = household_already_with_head_already_enrolled
    head_of_household_already_enrolled_program1.save()
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()

    enroll_households_to_program(
        Household.objects.filter(id=household_already_with_head_already_enrolled.id),
        enrollment_test_data["program2"],
        str(enrollment_test_data["user"].pk),
    )
    hh = Household.objects.order_by("created_at").last()
    assert hh_count + 1 == Household.objects.count()
    assert ind_count == Individual.objects.count()

    assert hh.head_of_household == head_of_household_already_enrolled_program2
    assert hh.program == enrollment_test_data["program2"]


@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_enroll_households_to_program_task(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()
    enroll_households_to_program_task(
        [str(enrollment_test_data["household_already_enrolled"].id)],
        str(enrollment_test_data["program2"].pk),
        str(enrollment_test_data["user"].pk),
    )
    assert hh_count == Household.objects.count()
    assert ind_count == Individual.objects.count()


@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_enroll_households_to_program_task_already_running(enrollment_test_data: dict) -> None:
    hh_count = Household.objects.count()
    ind_count = Individual.objects.count()

    task_params = {
        "task_name": "enroll_households_to_program_task",
        "household_ids": [str(enrollment_test_data["household"].id)],
        "program_for_enroll_id": str(enrollment_test_data["program2"].pk),
    }
    task_params_str = json.dumps(task_params, sort_keys=True)
    cache_key = hashlib.sha256(task_params_str.encode()).hexdigest()
    cache.set(cache_key, True, timeout=24 * 60 * 60)

    enroll_households_to_program_task(
        [str(enrollment_test_data["household"].id)],
        str(enrollment_test_data["program2"].pk),
        str(enrollment_test_data["user"].pk),
    )

    assert hh_count == Household.objects.count()
    assert ind_count == Individual.objects.count()

    cache.delete(cache_key)

    enroll_households_to_program_task(
        [str(enrollment_test_data["household"].id)],
        str(enrollment_test_data["program2"].pk),
        str(enrollment_test_data["user"].pk),
    )

    assert hh_count + 1 == Household.objects.count()
    assert ind_count + 2 == Individual.objects.count()


@patch("hope.apps.program.utils.randbelow")
def test_generate_rdi_unique_name_when_conflicts(mock_randbelow: Any, program1: Program) -> None:
    mock_randbelow.side_effect = [1111, 5555]
    RegistrationDataImportFactory(
        business_area=program1.business_area,
        name="RDI for enroll households to Programme: Program 1",
    )
    result = generate_rdi_unique_name(program1)
    expected_name = "RDI for enroll households to Programme: Program 1 (2111)"
    assert result == expected_name


@patch("hope.apps.program.utils.randbelow")
def test_generate_rdi_unique_name_no_conflicts(mock_randbelow: Any, program1: Program) -> None:
    mock_randbelow.return_value = 3333
    result = generate_rdi_unique_name(program1)
    expected_name = "RDI for enroll households to Programme: Program 1"
    assert result == expected_name
    assert not RegistrationDataImport.objects.filter(name=expected_name).exists()


@pytest.mark.parametrize(
    ("household_unicef_id", "error_message", "expected_substring"),
    [
        (
            "HH-001",
            'duplicate key value violates unique constraint "unique_if_not_removed_and_valid_for_representations"'
            " DETAIL: Key (document_number, country_id)=(123, AF) already exists.",
            "Document already exists: 123",
        ),
        (
            "HH-002",
            "some error message DETAIL: more info here",
            "some error message",
        ),
        (
            "HH-003",
            "simple error without detail keyword",
            "simple error without detail keyword",
        ),
    ],
)
def test_format_integrity_error(household_unicef_id: str, error_message: str, expected_substring: str) -> None:
    error = IntegrityError(error_message)
    result = _format_integrity_error(household_unicef_id, error)
    assert result.startswith(f"{household_unicef_id}: ")
    assert expected_substring in result


def test_create_enrollment_rdi_returns_merged_rdi(program1: Program, user: User) -> None:
    rdi = _create_enrollment_rdi(program1, str(user.pk))
    assert rdi.status == RegistrationDataImport.MERGED
    assert rdi.data_source == RegistrationDataImport.ENROLL_FROM_PROGRAM
    assert rdi.program == program1
    assert rdi.business_area == program1.business_area
    assert rdi.deduplication_engine_status is None


def test_create_enrollment_rdi_biometric_sets_dedup_pending(afghanistan: BusinessArea, user: User) -> None:
    program = ProgramFactory(business_area=afghanistan, biometric_deduplication_enabled=True)
    rdi = _create_enrollment_rdi(program, str(user.pk))
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_PENDING


@pytest.mark.usefixtures("mock_elasticsearch")
def test_prepare_and_save_household_copy_head_in_individuals_dict(
    program2: Program, household: Household, individual_hoh: Individual
) -> None:
    rdi = RegistrationDataImportFactory(business_area=program2.business_area, program=program2)
    new_individual = IndividualFactory(household=None, program=program2)
    individuals_dict = {individual_hoh.unicef_id: new_individual}

    original_id = household.id
    _prepare_and_save_household_copy(household, program2, rdi, individuals_dict, {})

    assert household.pk != original_id
    assert household.copied_from_id == original_id
    assert household.program == program2
    assert household.head_of_household == new_individual
    assert household.total_cash_received is None


@pytest.mark.usefixtures("mock_elasticsearch")
def test_prepare_and_save_household_copy_head_in_exclude_dict(
    program2: Program, household: Household, individual_hoh: Individual
) -> None:
    rdi = RegistrationDataImportFactory(business_area=program2.business_area, program=program2)
    target_individual = IndividualFactory(household=None, program=program2)
    individuals_to_exclude_dict = {str(individual_hoh.unicef_id): target_individual.id}

    original_id = household.id
    _prepare_and_save_household_copy(household, program2, rdi, {}, individuals_to_exclude_dict)

    assert household.pk != original_id
    assert household.copied_from_id == original_id
    assert household.head_of_household_id == target_individual.id
