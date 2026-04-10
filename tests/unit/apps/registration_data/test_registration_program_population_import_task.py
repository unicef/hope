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
from hope.apps.registration_data.celery_tasks import (
    registration_program_population_import_async_task,
    registration_program_population_import_async_task_action,
)
from hope.models import (
    AsyncRetryJob,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    RegistrationDataImport,
)

pytestmark = pytest.mark.usefixtures("mock_elasticsearch")


def run_registration_program_population_import_task(
    registration_data_import_id: str,
    business_area_id: str,
    import_from_program_id: str,
    import_to_program_id: str,
) -> bool:
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": registration_data_import_id,
            "business_area_id": business_area_id,
            "import_from_program_id": import_from_program_id,
            "import_to_program_id": import_to_program_id,
        }
    )
    return registration_program_population_import_async_task_action(job)


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

    run_registration_program_population_import_task(
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

    run_registration_program_population_import_task(
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
    run_registration_program_population_import_task(
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
        run_registration_program_population_import_task(
            str(rdi_id),
            str(business_area.id),
            str(programs["from"].id),
            str(programs["to"].id),
        )


@patch("hope.apps.registration_data.celery_tasks.handle_rdi_exception")
@patch("hope.apps.registration_data.celery_tasks.logger.warning")
@patch("hope.apps.registration_data.celery_tasks.RdiProgramPopulationCreateTask.execute")
def test_registration_program_population_import_task_handles_exception(
    mock_execute: Any,
    mock_warning: Any,
    mock_handle_rdi_exception: Any,
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
) -> None:
    registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
    registration_data_import.save()
    exc = RuntimeError("program population import failed")
    mock_execute.side_effect = exc

    with pytest.raises(RuntimeError, match="program population import failed"):
        run_registration_program_population_import_task(
            str(registration_data_import.id),
            str(business_area.id),
            str(programs["from"].id),
            str(programs["to"].id),
        )

    mock_warning.assert_called_once_with(exc)
    mock_handle_rdi_exception.assert_called_once_with(str(registration_data_import.id), exc)


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

    run_registration_program_population_import_task(
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

    run_registration_program_population_import_task(
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

    run_registration_program_population_import_task(
        str(registration_data_import.id),
        str(business_area.id),
        str(programs["from"].id),
        str(programs["to"].id),
    )

    registration_data_import.refresh_from_db()
    assert registration_data_import.status == RegistrationDataImport.IMPORT_SCHEDULED


def test_registration_program_population_import_task_queues_retry_job(
    business_area: Any,
    programs: dict[str, Any],
    registration_data_import: Any,
) -> None:
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        registration_program_population_import_async_task(
            registration_data_import,
            str(business_area.id),
            str(programs["from"].id),
            str(programs["to"].id),
        )

    job = AsyncRetryJob.objects.latest("pk")
    assert job.content_object == registration_data_import
    assert (
        job.action
        == "hope.apps.registration_data.celery_tasks.registration_program_population_import_async_task_action"
    )
    assert job.config == {
        "registration_data_import_id": str(registration_data_import.id),
        "business_area_id": str(business_area.id),
        "import_from_program_id": str(programs["from"].id),
        "import_to_program_id": str(programs["to"].id),
    }
    mock_queue.assert_called_once()
