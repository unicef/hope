import contextlib
from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import (
    ImportDataFactory,
    RegistrationDataImportFactory,
)
from hope.apps.generic_import.celery_tasks import process_generic_import_task
from hope.apps.generic_import.generic_upload_service.importer import format_validation_errors
from hope.apps.registration_datahub.exceptions import AlreadyRunningError
from hope.models import BusinessArea, Household, ImportData, Individual, Program, RegistrationDataImport


@pytest.mark.django_db
class TestProcessGenericImportTask:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        create_afghanistan()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.program = ProgramFactory(
            business_area=self.business_area,
            status=Program.ACTIVE,
        )
        self.user = UserFactory()

    def _create_import_objects(self):
        """Helper to create ImportData and RegistrationDataImport."""
        import_data = ImportDataFactory(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.XLSX,
        )

        rdi = RegistrationDataImportFactory(
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            business_area=self.business_area,
            program=self.program,
            imported_by=self.user,
            data_source=RegistrationDataImport.XLS,
            import_data=import_data,
            number_of_households=0,
            number_of_individuals=0,
        )

        return import_data, rdi

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_success_flow(self, mock_parser_class, mock_importer_class):
        """Test successful task execution with status transitions."""
        import_data, rdi = self._create_import_objects()

        # Mock parser
        mock_parser = Mock()
        mock_parser.households_data = []
        mock_parser.individuals_data = []
        mock_parser.documents_data = []
        mock_parser.accounts_data = []
        mock_parser.identities_data = []
        mock_parser_class.return_value = mock_parser

        # Mock importer
        mock_importer = Mock()
        mock_importer.import_data.return_value = []  # No errors
        mock_importer_class.return_value = mock_importer

        # Execute task
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

        # Verify status transitions
        import_data.refresh_from_db()
        rdi.refresh_from_db()

        assert import_data.status == ImportData.STATUS_FINISHED
        assert rdi.status == RegistrationDataImport.IN_REVIEW

        # Verify parser was called
        mock_parser_class.assert_called_once_with(business_area=rdi.business_area)
        mock_parser.parse.assert_called_once_with(import_data.file.path)

        # Verify importer was created and called
        assert mock_importer_class.called
        mock_importer.import_data.assert_called_once()

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_with_validation_errors(self, mock_parser_class, mock_importer_class):
        """Test task execution with validation errors."""
        import_data, rdi = self._create_import_objects()

        # Mock parser
        mock_parser = Mock()
        mock_parser.households_data = []
        mock_parser.individuals_data = []
        mock_parser.documents_data = []
        mock_parser.accounts_data = []
        mock_parser.identities_data = []
        mock_parser_class.return_value = mock_parser

        # Mock importer with errors
        mock_importer = Mock()
        validation_errors = [{"type": "document", "data": {}, "errors": {"field": ["Error message"]}}]
        mock_importer.import_data.return_value = validation_errors
        mock_importer_class.return_value = mock_importer

        # Execute task
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

        # Verify error status
        import_data.refresh_from_db()
        rdi.refresh_from_db()

        assert import_data.status == ImportData.STATUS_VALIDATION_ERROR
        assert import_data.validation_errors == str(validation_errors)
        assert rdi.status == RegistrationDataImport.IMPORT_ERROR
        assert "Validation errors" in rdi.error_message

    def test_task_with_already_running_error(self):
        """Test that AlreadyRunningError is raised when task is already running."""
        import_data, rdi = self._create_import_objects()

        # Mock locked_cache to return False (already locked)
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

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_updates_stats_on_success(self, mock_parser_class, mock_importer_class):
        """Test that household and individual counts are updated on success."""
        import_data, rdi = self._create_import_objects()

        # Mock parser
        mock_parser = Mock()
        mock_parser.households_data = []
        mock_parser.individuals_data = []
        mock_parser.documents_data = []
        mock_parser.accounts_data = []
        mock_parser.identities_data = []
        mock_parser_class.return_value = mock_parser

        # Mock importer
        mock_importer = Mock()
        mock_importer.import_data.return_value = []  # No errors
        mock_importer_class.return_value = mock_importer

        # Mock queryset counts
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

            # Execute task
            process_generic_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(import_data.id),
            )

        # Verify stats updated
        import_data.refresh_from_db()
        rdi.refresh_from_db()

        assert import_data.number_of_households == 5
        assert import_data.number_of_individuals == 15
        assert rdi.number_of_households == 5
        assert rdi.number_of_individuals == 15

    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_handles_parser_exception(self, mock_parser_class):
        """Test that parser exceptions are handled properly."""
        import_data, rdi = self._create_import_objects()

        # Mock parser to raise exception
        mock_parser_class.side_effect = RuntimeError("Parser error")

        # Create a mock for the task's retry method
        mock_task = Mock()
        mock_task.retry.side_effect = RuntimeError("Retry called")

        # Execute task and expect retry
        with pytest.raises(RuntimeError):
            process_generic_import_task.apply(
                args=[str(rdi.id), str(import_data.id)],
            ).get()

        # Verify error status was set
        import_data.refresh_from_db()
        rdi.refresh_from_db()

        assert import_data.status == ImportData.STATUS_ERROR
        assert rdi.status == RegistrationDataImport.IMPORT_ERROR

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_sets_status_to_running(self, mock_parser_class, mock_importer_class):
        """Test that task sets status to RUNNING at start."""
        import_data, rdi = self._create_import_objects()

        # Mock parser
        mock_parser = Mock()
        mock_parser.households_data = []
        mock_parser.individuals_data = []
        mock_parser.documents_data = []
        mock_parser.accounts_data = []
        mock_parser.identities_data = []
        mock_parser_class.return_value = mock_parser

        # Mock importer
        mock_importer = Mock()
        mock_importer.import_data.return_value = []
        mock_importer_class.return_value = mock_importer

        # Track status changes
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

        # Should have transitioned through RUNNING
        assert ImportData.STATUS_RUNNING in statuses

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_with_sentry_integration(self, mock_parser_class, mock_importer_class):
        """Test that Sentry captures exceptions."""
        import_data, rdi = self._create_import_objects()

        # Mock parser to raise exception
        mock_parser_class.side_effect = Exception("Test exception")

        # Mock sentry capture_exception
        with patch("hope.apps.generic_import.celery_tasks.capture_exception") as mock_sentry:
            mock_sentry.return_value = "test-sentry-id"

            with contextlib.suppress(Exception):
                process_generic_import_task.apply(
                    args=[str(rdi.id), str(import_data.id)],
                ).get()

            # Verify sentry was called
            assert mock_sentry.called

            # Verify sentry_id was saved
            rdi.refresh_from_db()
            assert rdi.sentry_id == "test-sentry-id"

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_sets_business_area_tag(self, mock_parser_class, mock_importer_class):
        """Test that Sentry business area tag is set."""
        import_data, rdi = self._create_import_objects()

        # Mock parser
        mock_parser = Mock()
        mock_parser.households_data = []
        mock_parser.individuals_data = []
        mock_parser.documents_data = []
        mock_parser.accounts_data = []
        mock_parser.identities_data = []
        mock_parser_class.return_value = mock_parser

        # Mock importer
        mock_importer = Mock()
        mock_importer.import_data.return_value = []
        mock_importer_class.return_value = mock_importer

        # Mock set_sentry_business_area_tag
        with patch("hope.apps.generic_import.celery_tasks.set_sentry_business_area_tag") as mock_sentry_tag:
            process_generic_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(import_data.id),
            )

            # Verify Sentry tag was set
            mock_sentry_tag.assert_called_once_with(self.business_area.name)

    @patch("hope.apps.generic_import.celery_tasks.Importer")
    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_passes_correct_data_to_importer(self, mock_parser_class, mock_importer_class):
        """Test that task passes all parser data to Importer."""
        import_data, rdi = self._create_import_objects()

        # Mock parser with test data
        mock_parser = Mock()
        mock_parser.households_data = [{"id": "h1"}]
        mock_parser.individuals_data = [{"id": "i1"}]
        mock_parser.documents_data = [{"id": "d1"}]
        mock_parser.accounts_data = [{"id": "a1"}]
        mock_parser.identities_data = [{"id": "id1"}]
        mock_parser_class.return_value = mock_parser

        # Mock importer
        mock_importer = Mock()
        mock_importer.import_data.return_value = []
        mock_importer_class.return_value = mock_importer

        # Execute task
        process_generic_import_task(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(import_data.id),
        )

        # Verify Importer was called with correct data
        mock_importer_class.assert_called_once_with(
            registration_data_import=rdi,
            households_data=[{"id": "h1"}],
            individuals_data=[{"id": "i1"}],
            documents_data=[{"id": "d1"}],
            accounts_data=[{"id": "a1"}],
            identities_data=[{"id": "id1"}],
        )

    def test_locked_cache_key_format(self):
        """Test that locked_cache uses correct key format."""
        import_data, rdi = self._create_import_objects()

        # Track the cache key used
        cache_keys = []

        @contextlib.contextmanager
        def track_cache_key(key, **kwargs):
            cache_keys.append(key)
            yield True

        with (
            patch(
                "hope.apps.generic_import.celery_tasks.locked_cache",
                new=track_cache_key,
            ),
            patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser"),
            patch("hope.apps.generic_import.celery_tasks.Importer"),
        ):
            # Mock parser and importer
            with patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser") as mock_parser_class:
                mock_parser = Mock()
                mock_parser.households_data = []
                mock_parser.individuals_data = []
                mock_parser.documents_data = []
                mock_parser.accounts_data = []
                mock_parser.identities_data = []
                mock_parser_class.return_value = mock_parser

                with patch("hope.apps.generic_import.celery_tasks.Importer") as mock_importer_class:
                    mock_importer = Mock()
                    mock_importer.import_data.return_value = []
                    mock_importer_class.return_value = mock_importer

                    process_generic_import_task(
                        registration_data_import_id=str(rdi.id),
                        import_data_id=str(import_data.id),
                    )

        # Verify cache key format
        assert len(cache_keys) == 1
        assert cache_keys[0] == f"process_generic_import_task-{rdi.id}"

    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_handles_sentry_capture_exception_failure(self, mock_parser_class):
        """Test that task continues when Sentry capture_exception itself fails."""
        import_data, rdi = self._create_import_objects()
        mock_parser_class.side_effect = RuntimeError("Test error")

        with patch("hope.apps.generic_import.celery_tasks.capture_exception") as mock_sentry:
            mock_sentry.side_effect = Exception("Sentry failed")

            with contextlib.suppress(Exception):
                process_generic_import_task.apply(
                    args=[str(rdi.id), str(import_data.id)],
                ).get()

        rdi.refresh_from_db()
        assert rdi.sentry_id == "N/A"

    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_handles_import_data_update_failure_in_error_handler(self, mock_parser_class):
        """Test that task continues when ImportData status update fails in error handler."""
        import_data, rdi = self._create_import_objects()
        mock_parser_class.side_effect = RuntimeError("Test error")

        original_get = ImportData.objects.get

        call_count = [0]

        def mock_get(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:  # First two calls succeed (main try block)
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

        # RDI should still be updated even if ImportData update failed
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORT_ERROR

    @patch("hope.apps.generic_import.celery_tasks.XlsxSomaliaParser")
    def test_task_handles_rdi_update_failure_in_error_handler(self, mock_parser_class):
        """Test that task continues when RDI status update fails in error handler."""
        import_data, rdi = self._create_import_objects()
        mock_parser_class.side_effect = RuntimeError("Test error")

        original_get = RegistrationDataImport.objects.get

        call_count = [0]

        def mock_get(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:  # First two calls succeed (main try block)
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

        # ImportData should still be updated even if RDI update failed
        import_data.refresh_from_db()
        assert import_data.status == ImportData.STATUS_ERROR


class TestFormatValidationErrors:
    """Tests for format_validation_errors() function."""

    def test_empty_errors_list(self):
        """Test that empty errors list returns 'No errors'."""
        result = format_validation_errors([])
        assert result == "No errors"

    def test_non_dict_error_item(self):
        """Test handling of non-dict error items (e.g., string errors)."""
        errors = ["Simple error message", "Another error"]
        result = format_validation_errors(errors)
        assert "1. Simple error message" in result
        assert "2. Another error" in result

    def test_household_error_type(self):
        """Test formatting of household error type."""
        errors = [
            {
                "type": "household",
                "data": {"id": "abc12345-full-uuid-here"},
                "errors": {"size": ["Must be positive"]},
            }
        ]
        result = format_validation_errors(errors)
        assert "Household (ID: abc12345...)" in result
        assert "size: Must be positive" in result

    def test_individual_error_type(self):
        """Test formatting of individual error type."""
        errors = [
            {
                "type": "individual",
                "data": {"full_name": "John Doe", "given_name": "John"},
                "errors": {"birth_date": ["Invalid date format"]},
            }
        ]
        result = format_validation_errors(errors)
        assert "Individual (John Doe)" in result
        assert "birth_date: Invalid date format" in result

    def test_individual_error_type_fallback_to_given_name(self):
        """Test individual error falls back to given_name when full_name is missing."""
        errors = [
            {
                "type": "individual",
                "data": {"given_name": "Jane"},
                "errors": {"sex": ["Required field"]},
            }
        ]
        result = format_validation_errors(errors)
        assert "Individual (Jane)" in result

    def test_account_error_type(self):
        """Test formatting of account error type."""
        errors = [
            {
                "type": "account",
                "data": {"number": "+252612345678"},
                "errors": {"account_type": ["Unknown type"]},
            }
        ]
        result = format_validation_errors(errors)
        assert "Account (+252612345678)" in result
        assert "account_type: Unknown type" in result

    def test_unknown_error_type(self):
        """Test formatting of unknown/other error type."""
        errors = [
            {
                "type": "document",
                "data": {},
                "errors": {"type": ["Required"]},
            }
        ]
        result = format_validation_errors(errors)
        assert "Document" in result
        assert "type: Required" in result

    def test_field_errors_as_string(self):
        """Test handling of field errors as string instead of list."""
        errors = [
            {
                "type": "household",
                "data": {"id": "12345678"},
                "errors": {"village": "This field is required"},
            }
        ]
        result = format_validation_errors(errors)
        assert "village: This field is required" in result

    def test_multiple_field_errors(self):
        """Test formatting of multiple field errors."""
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

    def test_missing_data_fields(self):
        """Test handling when data fields are missing."""
        errors = [
            {
                "type": "household",
                "data": {},  # No id field
                "errors": {"size": ["Required"]},
            },
            {
                "type": "individual",
                "data": {},  # No full_name or given_name
                "errors": {"name": ["Required"]},
            },
            {
                "type": "account",
                "data": {},  # No number field
                "errors": {"number": ["Required"]},
            },
        ]
        result = format_validation_errors(errors)
        # Should use "Unknown" for missing identifiers
        assert "Household (ID: Unknown...)" in result
        assert "Individual (Unknown)" in result
        assert "Account (Unknown)" in result
