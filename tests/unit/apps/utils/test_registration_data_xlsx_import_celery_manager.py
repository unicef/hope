from unittest import mock

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ImportDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.models import RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_areas():
    return {
        "afghanistan": BusinessAreaFactory(slug="afghanistan", name="Afghanistan"),
        "sudan": BusinessAreaFactory(slug="sudan", name="Sudan"),
    }


@pytest.fixture
def programs(business_areas):
    return {key: ProgramFactory(business_area=area) for key, area in business_areas.items()}


@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_querysets(mock_get_all_tasks, programs) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    manager = RegistrationDataXlsxImportCeleryManager()
    program = programs["afghanistan"]
    rdi_import_scheduled = RegistrationDataImportFactory(
        name="IMPORT_SCHEDULED",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    rdi_importing = RegistrationDataImportFactory(
        name="IMPORTING",
        status=RegistrationDataImport.IMPORTING,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="IMPORT_ERROR",
        status=RegistrationDataImport.IMPORT_ERROR,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="REFUSED_IMPORT",
        status=RegistrationDataImport.REFUSED_IMPORT,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="DEDUPLICATION",
        status=RegistrationDataImport.DEDUPLICATION,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="DEDUPLICATION_FAILED",
        status=RegistrationDataImport.DEDUPLICATION_FAILED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="MERGE_SCHEDULED",
        status=RegistrationDataImport.MERGE_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="MERGING",
        status=RegistrationDataImport.MERGING,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="MERGE_ERROR",
        status=RegistrationDataImport.MERGE_ERROR,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    RegistrationDataImportFactory(
        name="MERGED",
        status=RegistrationDataImport.MERGED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
    )
    assert manager.pending_queryset.count() == 1
    assert manager.pending_queryset.first() == rdi_import_scheduled
    assert manager.in_progress_queryset.count() == 1
    assert manager.in_progress_queryset.first() == rdi_importing


@mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_add_scheduled_to_queue(
    mock_get_all_celery_tasks: mock.MagicMock,
    mock_registration_xlsx_import_task_delay: mock.MagicMock,
    programs,
) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    mock_get_all_celery_tasks.return_value = []
    program = programs["afghanistan"]

    import_data = ImportDataFactory()
    rdi = RegistrationDataImportFactory(
        name="IMPORT_SCHEDULED",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
        import_data=import_data,
    )
    manager = RegistrationDataXlsxImportCeleryManager()
    manager.execute()
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert mock_registration_xlsx_import_task_delay.call_count == 1
    mock_registration_xlsx_import_task_delay.assert_called_with(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(rdi.import_data_id),
        business_area_id=str(rdi.business_area_id),
        program_id=str(rdi.program_id),
    )


@mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_revert_status_rdi_with_importing_status(
    mock_get_all_celery_tasks: mock.MagicMock,
    mock_registration_xlsx_import_task_delay: mock.MagicMock,
    programs,
) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    mock_get_all_celery_tasks.return_value = []
    program = programs["afghanistan"]

    import_data = ImportDataFactory()
    rdi = RegistrationDataImportFactory(
        name="IMPORTING",
        status=RegistrationDataImport.IMPORTING,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
        import_data=import_data,
    )
    manager = RegistrationDataXlsxImportCeleryManager()
    manager.execute()
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert mock_registration_xlsx_import_task_delay.call_count == 1
    mock_registration_xlsx_import_task_delay.assert_called_with(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(rdi.import_data_id),
        business_area_id=str(rdi.business_area_id),
        program_id=str(rdi.program_id),
    )


@mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_not_start_importing_tasks(
    mock_get_all_celery_tasks: mock.MagicMock,
    mock_registration_xlsx_import_task_delay: mock.MagicMock,
    programs,
) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    program = programs["afghanistan"]
    import_data = ImportDataFactory()
    rdi = RegistrationDataImportFactory(
        name="IMPORTING",
        status=RegistrationDataImport.IMPORTING,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
        import_data=import_data,
    )
    kwargs = {
        "registration_data_import_id": str(rdi.id),
        "import_data_id": str(rdi.import_data_id),
        "business_area_id": str(rdi.business_area_id),
        "program_id": str(rdi.program_id),
    }

    mock_get_all_celery_tasks.return_value = [
        {
            "name": "hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
            "kwargs": kwargs,
            "status": "active",
        }
    ]
    manager = RegistrationDataXlsxImportCeleryManager()
    manager.execute()
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORTING
    assert mock_registration_xlsx_import_task_delay.call_count == 0


@mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_not_start_already_scheduled(
    mock_get_all_celery_tasks: mock.MagicMock,
    mock_registration_xlsx_import_task_delay: mock.MagicMock,
    programs,
) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    program = programs["afghanistan"]
    import_data = ImportDataFactory()
    rdi = RegistrationDataImportFactory(
        name="IMPORT_SCHEDULED",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        program=program,
        business_area=program.business_area,
        import_data=import_data,
    )
    kwargs = {
        "registration_data_import_id": str(rdi.id),
        "import_data_id": str(rdi.import_data_id),
        "business_area_id": str(rdi.business_area_id),
        "program_id": str(rdi.program_id),
    }

    mock_get_all_celery_tasks.return_value = [
        {
            "name": "hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
            "kwargs": kwargs,
            "status": "queued",
        }
    ]
    manager = RegistrationDataXlsxImportCeleryManager()
    manager.execute()
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert mock_registration_xlsx_import_task_delay.call_count == 0


@mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
@mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
def test_parametrized_by_business_area(
    mock_get_all_celery_tasks: mock.MagicMock,
    mock_registration_xlsx_import_task_delay: mock.MagicMock,
    business_areas,
    programs,
) -> None:
    from hope.apps.utils.celery_manager import RegistrationDataXlsxImportCeleryManager

    program = programs["afghanistan"]
    import_data = ImportDataFactory()
    rdi = RegistrationDataImportFactory(
        name="IMPORT_SCHEDULED afghanistan",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        business_area=business_areas["afghanistan"],
        program=program,
        import_data=import_data,
    )

    import_data2 = ImportDataFactory()
    RegistrationDataImportFactory(
        name="IMPORT_SCHEDULED sudan",
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        data_source=RegistrationDataImport.XLS,
        business_area=business_areas["sudan"],
        program=programs["sudan"],
        import_data=import_data2,
    )

    mock_get_all_celery_tasks.return_value = []
    manager = RegistrationDataXlsxImportCeleryManager(business_area=business_areas["afghanistan"])
    manager.execute()
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert mock_registration_xlsx_import_task_delay.call_count == 1
    mock_registration_xlsx_import_task_delay.assert_called_with(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(rdi.import_data_id),
        business_area_id=str(rdi.business_area_id),
        program_id=str(rdi.program_id),
    )
