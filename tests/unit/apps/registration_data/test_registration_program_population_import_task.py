from typing import Any
from unittest.mock import patch

import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, CountryFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.registration_data.celery_tasks import registration_program_population_import_task
from hope.models import (
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    RegistrationDataImport,
)

pytestmark = pytest.mark.usefixtures("mock_elasticsearch")


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def programs(business_area: Any) -> dict[str, Any]:
    program_from = ProgramFactory(business_area=business_area)
    program_to = ProgramFactory(business_area=business_area)
    return {"from": program_from, "to": program_to}


@pytest.fixture
def registration_data_import(business_area: Any, programs: dict[str, Any]) -> Any:
    return RegistrationDataImportFactory(business_area=business_area, program=programs["to"])


@pytest.fixture
def rdi_other(business_area: Any, programs: dict[str, Any]) -> Any:
    return RegistrationDataImportFactory(business_area=business_area, program=programs["from"])


@pytest.fixture
def admin_areas() -> dict[str, Any]:
    return {
        "admin1": AreaFactory(),
        "admin2": AreaFactory(),
        "admin3": AreaFactory(),
        "admin4": AreaFactory(),
    }


@pytest.fixture
def population_source(
    admin_areas: dict[str, Any],
    business_area: Any,
    programs: dict[str, Any],
    rdi_other: Any,
) -> dict[str, Any]:
    household = HouseholdFactory(
        registration_data_import=rdi_other,
        business_area=business_area,
        program=programs["from"],
        admin1=admin_areas["admin1"],
        admin2=admin_areas["admin2"],
        admin3=admin_areas["admin3"],
        admin4=admin_areas["admin4"],
        detail_id="1234567890",
        flex_fields={"enumerator_id": "123", "some": "thing"},
        create_role=False,
    )
    second_individual = IndividualFactory(
        household=household,
        business_area=business_area,
        program=programs["from"],
        registration_data_import=rdi_other,
    )
    role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=second_individual,
        role=ROLE_PRIMARY,
    )
    country = CountryFactory()
    document_type = DocumentTypeFactory(key="birth_certificate")
    document = DocumentFactory(
        individual=household.head_of_household,
        program=programs["from"],
        type=document_type,
        country=country,
    )
    identity = IndividualIdentityFactory(
        individual=household.head_of_household,
        country=country,
        partner=PartnerFactory(),
    )
    return {
        "household": household,
        "individuals": [household.head_of_household, second_individual],
        "role": role,
        "document": document,
        "identity": identity,
    }


def test_registration_program_population_import_task_wrong_status(
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
) -> None:
    status_before = registration_data_import.status

    registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == status_before


def test_registration_program_population_import_task(
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
    population_source: dict[str, Any],
) -> None:
    business_area.postpone_deduplication = True
    business_area.save()
    registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
    registration_data_import.save()

    assert Household.pending_objects.count() == 0
    assert Individual.pending_objects.count() == 0
    assert IndividualIdentity.pending_objects.count() == 0
    assert Document.pending_objects.count() == 0
    assert IndividualRoleInHousehold.pending_objects.count() == 0

    registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW
    assert Household.pending_objects.count() == 1
    assert Individual.pending_objects.count() == 2
    assert IndividualIdentity.pending_objects.count() == 1
    assert Document.pending_objects.count() == 1
    assert IndividualRoleInHousehold.pending_objects.count() == 1

    registration_data_import2 = RegistrationDataImportFactory(
        name="Other",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=programs["to"],
    )
    registration_program_population_import_task(
        str(registration_data_import2.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    assert Household.pending_objects.count() == 1
    assert Individual.pending_objects.count() == 2
    assert IndividualIdentity.pending_objects.count() == 1
    assert Document.pending_objects.count() == 1
    assert IndividualRoleInHousehold.pending_objects.count() == 1


def test_registration_program_population_import_task_error(
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
) -> None:
    rdi_id = registration_data_import.id
    registration_data_import.delete()

    with pytest.raises(RegistrationDataImport.DoesNotExist):
        registration_program_population_import_task(
            str(rdi_id),
            str(business_area.id),
            str(programs["from"].id),
            str(programs["to"].id),
        )


def test_registration_program_population_import_ba_postpone_deduplication(
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
    population_source: dict[str, Any],
) -> None:
    business_area.postpone_deduplication = True
    business_area.save()
    registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
    registration_data_import.save()

    registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW


@patch("hope.apps.registration_data.tasks.rdi_program_population_create.DeduplicateTask")
def test_registration_program_population_import_with_deduplication(
    mock_dedupe_task: Any,
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
    population_source: dict[str, Any],
) -> None:
    business_area.postpone_deduplication = False
    business_area.save()
    registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
    registration_data_import.save()

    registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == RegistrationDataImport.DEDUPLICATION
    mock_dedupe_task.assert_called_once()
    mock_dedupe_task.return_value.deduplicate_pending_individuals.assert_called_once()


@patch("hope.apps.registration_data.celery_tasks.locked_cache")
def test_registration_program_population_import_locked_cache(
    mocked_locked_cache: Any,
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
) -> None:
    mocked_locked_cache.return_value.__enter__.return_value = False
    registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
    registration_data_import.save()

    registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == RegistrationDataImport.IMPORT_SCHEDULED
