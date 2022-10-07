import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
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
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

        cls.business_area = BusinessArea.objects.first()

        cls._create_submission_with_merged_rdi()
        cls._create_submission_with_merged_rdi()
        cls._create_submission_with_in_review_rdi()

    def test_mark_submissions(self):
        task = MarkSubmissions(self.business_area)
        task.execute()

        self.assertEqual(KoboImportedSubmission.objects.filter(amended=True).count(), 1)

    @classmethod
    def _create_submission_with_in_review_rdi(cls):
        cls._create_submission("IN_REVIEW")

    @classmethod
    def _create_submission_with_merged_rdi(cls):
        cls._create_submission("MERGED")

    @classmethod
    def _create_submission(cls, status):
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/kobo_submissions.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )
        datahub_id = uuid.uuid4()

        registration_data_import = RegistrationDataImportFactory(status=status, datahub_id=datahub_id)
        registration_data_import_data_hub = RegistrationDataImportDatahubFactory(
            id=datahub_id,
            import_data=import_data,
            business_area_slug=cls.business_area.slug,
            hct_id=registration_data_import.pk,
        )

        submission_uuid = uuid.uuid4()
        imported_household = ImportedHouseholdFactory(
            registration_data_import=registration_data_import_data_hub,
            kobo_submission_uuid=submission_uuid,
        )
        KoboImportedSubmission.objects.create(
            registration_data_import=registration_data_import_data_hub,
            kobo_submission_uuid=submission_uuid,
            kobo_asset_id="test",
            kobo_submission_time=timezone.now(),
            imported_household=imported_household,
        )
