import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import ImportData, KoboImportedSubmission
from hct_mis_api.apps.registration_data.services.mark_submissions import MarkSubmissions
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import HouseholdFactory
from tests.extras.test_utils.factories.registration_data import (
    RegistrationDataImportFactory,
)


class TestMarkSubmissions(TestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

        cls.business_area = BusinessArea.objects.first()

        cls._create_submission_with_merged_rdi()
        cls._create_submission_with_merged_rdi()
        cls._create_submission_with_in_review_rdi()

    def test_mark_submissions(self) -> None:
        task = MarkSubmissions(self.business_area)
        task.execute()

        self.assertEqual(KoboImportedSubmission.objects.filter(amended=True).count(), 1)

    @classmethod
    def _create_submission_with_in_review_rdi(cls) -> None:
        cls._create_submission("IN_REVIEW")

    @classmethod
    def _create_submission_with_merged_rdi(cls) -> None:
        cls._create_submission("MERGED")

    @classmethod
    def _create_submission(cls, status: str) -> None:
        content = Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/kobo_submissions.json").read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )

        registration_data_import = RegistrationDataImportFactory(status=status, import_data=import_data)

        submission_uuid = uuid.uuid4()
        imported_household = HouseholdFactory(
            registration_data_import=registration_data_import,
            kobo_submission_uuid=submission_uuid,
        )
        KoboImportedSubmission.objects.create(
            registration_data_import=registration_data_import,
            kobo_submission_uuid=submission_uuid,
            kobo_asset_id="test",
            kobo_submission_time=timezone.now(),
            imported_household=imported_household,
        )
