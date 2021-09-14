import datetime
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedHouseholdFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    KoboImportedSubmission,
)
from hct_mis_api.apps.registration_datahub.tasks.mark_submissions import MarkSubmissions


class TestMarkSubmissions(TestCase):
    multi_db = True

    def setUp(self) -> None:
        call_command("loadbusinessareas")

        self.business_area = BusinessArea.objects.first()
        self.business_area.custom_fields = {"ignore_amended_kobo_submissions": False}
        self.business_area.save()

        self._create_submission_with_merged_rdi()
        self._create_submission_with_merged_rdi()
        self._create_submission_with_not_started_rdi()

    def test_mark_submissions(self):
        task = MarkSubmissions(self.business_area)
        task.execute()

        self.assertEqual(KoboImportedSubmission.objects.filter(amended=True).count(), 1)

    def _create_submission_with_not_started_rdi(self):
        self._create_submission("NOT_STARTED")

    def _create_submission_with_merged_rdi(self):
        self._create_submission("DONE")

    def _create_submission(self, import_dane):
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/kobo_submissions.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )
        registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=import_data, business_area_slug=self.business_area.slug, import_done=import_dane
        )
        submission_uuid = uuid.uuid4()
        imported_household = ImportedHouseholdFactory(
            registration_data_import=registration_data_import,
            kobo_submission_uuid=submission_uuid,
        )
        KoboImportedSubmission.objects.create(
            registration_data_import=registration_data_import,
            kobo_submission_uuid=submission_uuid,
            kobo_asset_id="test",
            kobo_submission_time=datetime.datetime.now(),
            imported_household=imported_household,
        )
