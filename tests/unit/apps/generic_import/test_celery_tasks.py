from collections.abc import Generator
import contextlib
from unittest.mock import MagicMock, Mock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ImportDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.generic_import.celery_tasks import process_generic_import_task
from hope.apps.generic_import.generic_upload_service.importer import format_validation_errors
from hope.apps.registration_datahub.exceptions import AlreadyRunningError
from hope.models import BusinessArea, Household, ImportData, Individual, Program, RegistrationDataImport, User


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def import_data(business_area) -> ImportData:
    return ImportDataFactory(
        status=ImportData.STATUS_PENDING,
        business_area_slug=business_area.slug,
        data_type=ImportData.XLSX,
    )


@pytest.fixture
def rdi(business_area, program, user, import_data) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
        imported_by=user,
        data_source=RegistrationDataImport.XLS,
        import_data=import_data,
        number_of_households=0,
        number_of_individuals=0,
    )


@pytest.fixture
def mock_parser_class() -> Generator[MagicMock, None, None]:
    with patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser") as mock_cls:
        parser = Mock()
        parser.households_data = []
        parser.individuals_data = []
        parser.documents_data = []
        parser.accounts_data = []
        parser.identities_data = []
        mock_cls.return_value = parser
        yield mock_cls


@pytest.fixture
def mock_importer_class() -> Generator[MagicMock, None, None]:
    with patch("hope.apps.generic_import.celery_tasks.Importer") as mock_cls:
        importer = Mock()
        importer.import_data.return_value = []
        mock_cls.return_value = importer
        yield mock_cls


def test_format_validation_errors_returns_no_errors_for_empty_list():
    result = format_validation_errors([])
    assert result == "No errors"


def test_format_validation_errors_formats_non_dict_items():
    errors = ["Simple error message", "Another error"]
    result = format_validation_errors(errors)
    assert "1. Simple error message" in result
    assert "2. Another error" in result


@pytest.mark.parametrize(
    ("error_type", "data", "expected_label"),
    [
        ("household", {"id": "abc12345-full-uuid-here"}, "Household (ID: abc12345...)"),
        ("individual", {"full_name": "John Doe", "given_name": "John"}, "Individual (John Doe)"),
        ("account", {"number": "+252612345678"}, "Account (+252612345678)"),
        ("document", {}, "Document"),
    ],
    ids=["household", "individual", "account", "document"],
)
def test_format_validation_errors_formats_error_type_label(error_type, data, expected_label):
    errors = [
        {
            "type": error_type,
            "data": data,
            "errors": {"field": ["Error message"]},
        }
    ]
    result = format_validation_errors(errors)
    assert expected_label in result
    assert "field: Error message" in result


def test_format_validation_errors_falls_back_to_given_name_for_individual():
    errors = [
        {
            "type": "individual",
            "data": {"given_name": "Jane"},
            "errors": {"sex": ["Required field"]},
        }
    ]
    result = format_validation_errors(errors)
    assert "Individual (Jane)" in result


def test_format_validation_errors_handles_field_errors_as_string():
    errors = [
        {
            "type": "household",
            "data": {"id": "12345678"},
            "errors": {"village": "This field is required"},
        }
    ]
    result = format_validation_errors(errors)
    assert "village: This field is required" in result


def test_format_validation_errors_formats_multiple_field_errors():
    errors = [
        {
            "type": "individual",
            "data": {"full_name": "Test Person"},
            "errors": {
                "birth_date": ["Invalid format", "Cannot be in future"],
                "sex": ["Required field"],
            },
        }
    ]
    result = format_validation_errors(errors)
    assert "birth_date: Invalid format" in result
    assert "birth_date: Cannot be in future" in result
    assert "sex: Required field" in result


@pytest.mark.parametrize(
    ("error_type", "expected_identifier"),
    [
        ("household", "Household (ID: Unknown...)"),
        ("individual", "Individual (Unknown)"),
        ("account", "Account (Unknown)"),
    ],
    ids=["household", "individual", "account"],
)
def test_format_validation_errors_uses_unknown_for_missing_identifier(error_type, expected_identifier):
    errors = [
        {
            "type": error_type,
            "data": {},
            "errors": {"field": ["Required"]},
        }
    ]
    result = format_validation_errors(errors)
    assert expected_identifier in result


@pytest.mark.django_db
def test_process_generic_import_task_sets_finished_and_in_review_on_success(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    process_generic_import_task(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(import_data.id),
    )

    import_data.refresh_from_db()
    rdi.refresh_from_db()

    assert import_data.status == ImportData.STATUS_FINISHED
    assert rdi.status == RegistrationDataImport.IN_REVIEW

    mock_parser_class.assert_called_once_with(business_area=rdi.business_area)
    mock_parser_class.return_value.parse.assert_called_once_with(import_data.file.path)
    assert mock_importer_class.called
    mock_importer_class.return_value.import_data.assert_called_once()


@pytest.mark.django_db
def test_process_generic_import_task_sets_error_status_on_validation_errors(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    validation_errors = [{"type": "document", "data": {}, "errors": {"field": ["Error message"]}}]
    mock_importer_class.return_value.import_data.return_value = validation_errors

    process_generic_import_task(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(import_data.id),
    )

    import_data.refresh_from_db()
    rdi.refresh_from_db()

    assert import_data.status == ImportData.STATUS_VALIDATION_ERROR
    assert import_data.validation_errors == str(validation_errors)
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR
    assert "Validation errors" in rdi.error_message


@pytest.mark.django_db
def test_process_generic_import_task_raises_already_running_error(import_data, rdi):
    @contextlib.contextmanager
    def mock_locked_cache(*args, **kwargs):
        yield False

    with patch(
        "hope.apps.generic_import.celery_tasks.locked_cache",
        new=mock_locked_cache,
    ):
        with pytest.raises(AlreadyRunningError) as exc_info:
            process_generic_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(import_data.id),
            )

        assert "is already running" in str(exc_info.value)


@pytest.mark.django_db
def test_process_generic_import_task_updates_household_and_individual_counts(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    with (
        patch.object(Household.pending_objects, "filter") as mock_household_filter,
        patch.object(Individual.pending_objects, "filter") as mock_individual_filter,
    ):
        mock_household_qs = Mock()
        mock_household_qs.count.return_value = 5
        mock_household_filter.return_value = mock_household_qs

        mock_individual_qs = Mock()
        mock_individual_qs.count.return_value = 15
        mock_individual_filter.return_value = mock_individual_qs

        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

    import_data.refresh_from_db()
    rdi.refresh_from_db()

    assert import_data.number_of_households == 5
    assert import_data.number_of_individuals == 15
    assert rdi.number_of_households == 5
    assert rdi.number_of_individuals == 15


@pytest.mark.django_db
def test_process_generic_import_task_handles_parser_exception(import_data, rdi, mock_parser_class):
    mock_parser_class.side_effect = RuntimeError("Parser error")

    with pytest.raises(RuntimeError):
        process_generic_import_task.apply(
            args=[str(rdi.id), str(import_data.id)],
        ).get()

    import_data.refresh_from_db()
    rdi.refresh_from_db()

    assert import_data.status == ImportData.STATUS_ERROR
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR


@pytest.mark.django_db
def test_process_generic_import_task_transitions_through_running_status(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    statuses = []
    original_save = ImportData.save

    def track_status(self, *args, **kwargs):
        statuses.append(self.status)
        return original_save(self, *args, **kwargs)

    with patch.object(ImportData, "save", track_status):
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

    assert ImportData.STATUS_RUNNING in statuses


@pytest.mark.django_db
def test_process_generic_import_task_captures_exception_to_sentry(import_data, rdi, mock_parser_class):
    mock_parser_class.side_effect = Exception("Test exception")

    with patch("hope.apps.generic_import.celery_tasks.capture_exception") as mock_sentry:
        mock_sentry.return_value = "test-sentry-id"

        with contextlib.suppress(Exception):
            process_generic_import_task.apply(
                args=[str(rdi.id), str(import_data.id)],
            ).get()

        assert mock_sentry.called

        rdi.refresh_from_db()
        assert rdi.sentry_id == "test-sentry-id"


@pytest.mark.django_db
def test_process_generic_import_task_sets_sentry_business_area_tag(
    business_area, import_data, rdi, mock_parser_class, mock_importer_class
):
    with patch("hope.apps.generic_import.celery_tasks.set_sentry_business_area_tag") as mock_sentry_tag:
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

        mock_sentry_tag.assert_called_once_with(business_area.name)


@pytest.mark.django_db
def test_process_generic_import_task_passes_parsed_data_to_importer(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    parser = mock_parser_class.return_value
    parser.households_data = [{"id": "h1"}]
    parser.individuals_data = [{"id": "i1"}]
    parser.documents_data = [{"id": "d1"}]
    parser.accounts_data = [{"id": "a1"}]
    parser.identities_data = [{"id": "id1"}]

    process_generic_import_task(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(import_data.id),
    )

    mock_importer_class.assert_called_once_with(
        registration_data_import=rdi,
        households_data=[{"id": "h1"}],
        individuals_data=[{"id": "i1"}],
        documents_data=[{"id": "d1"}],
        accounts_data=[{"id": "a1"}],
        identities_data=[{"id": "id1"}],
    )


@pytest.mark.django_db
def test_process_generic_import_task_uses_correct_cache_key_format(
    import_data, rdi, mock_parser_class, mock_importer_class
):
    cache_keys = []

    @contextlib.contextmanager
    def track_cache_key(key, **kwargs):
        cache_keys.append(key)
        yield True

    with patch("hope.apps.generic_import.celery_tasks.locked_cache", new=track_cache_key):
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

    assert len(cache_keys) == 1
    assert cache_keys[0] == f"process_generic_import_task-{rdi.id}"


@pytest.mark.django_db
def test_process_generic_import_task_handles_sentry_capture_failure(import_data, rdi, mock_parser_class):
    mock_parser_class.side_effect = RuntimeError("Test error")

    with patch("hope.apps.generic_import.celery_tasks.capture_exception") as mock_sentry:
        mock_sentry.side_effect = Exception("Sentry failed")

        with contextlib.suppress(Exception):
            process_generic_import_task.apply(
                args=[str(rdi.id), str(import_data.id)],
            ).get()

    rdi.refresh_from_db()
    assert rdi.sentry_id == "N/A"


@pytest.mark.django_db
def test_process_generic_import_task_updates_import_data_despite_rdi_update_failure(
    import_data, rdi, mock_parser_class
):
    mock_parser_class.side_effect = RuntimeError("Test error")

    original_get = RegistrationDataImport.objects.get
    call_count = [0]

    def mock_get(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] <= 2:
            return original_get(*args, **kwargs)
        raise Exception("DB error in error handler")

    with (
        patch("hope.apps.generic_import.celery_tasks.capture_exception", return_value="sentry-123"),
        patch.object(RegistrationDataImport.objects, "get", side_effect=mock_get),
    ):
        with contextlib.suppress(Exception):
            process_generic_import_task.apply(
                args=[str(rdi.id), str(import_data.id)],
            ).get()

    import_data.refresh_from_db()
    assert import_data.status == ImportData.STATUS_ERROR


@pytest.mark.django_db
def test_process_generic_import_task_updates_rdi_despite_import_data_update_failure(
    import_data, rdi, mock_parser_class
):
    mock_parser_class.side_effect = RuntimeError("Test error")

    original_get = ImportData.objects.get
    call_count = [0]

    def mock_get(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] <= 2:
            return original_get(*args, **kwargs)
        raise Exception("DB error in error handler")

    with (
        patch("hope.apps.generic_import.celery_tasks.capture_exception", return_value="sentry-123"),
        patch.object(ImportData.objects, "get", side_effect=mock_get),
    ):
        with contextlib.suppress(Exception):
            process_generic_import_task.apply(
                args=[str(rdi.id), str(import_data.id)],
            ).get()

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR
