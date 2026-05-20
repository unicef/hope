from io import BytesIO
from pathlib import Path
import uuid

from django.conf import settings
from django.core.files import File
from django.utils import timezone
import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, RegistrationDataImportFactory
from hope.apps.registration_data.services.mark_submissions import MarkSubmissions
from hope.models import BusinessArea, ImportData, KoboImportedSubmission, RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


def _make_submission(business_area: BusinessArea, status: str) -> None:
    content = Path(f"{settings.TESTS_ROOT}/apps/registration_data/test_file/kobo_submissions.json").read_bytes()
    file = File(BytesIO(content), name="kobo_submissions.json")
    import_data = ImportData.objects.create(
        file=file,
        number_of_households=1,
        number_of_individuals=2,
    )
    registration_data_import = RegistrationDataImportFactory(
        status=status,
        import_data=import_data,
        business_area=business_area,
    )
    submission_uuid = uuid.uuid4()
    imported_household = HouseholdFactory(
        registration_data_import=registration_data_import,
        kobo_submission_uuid=submission_uuid,
        business_area=business_area,
    )
    KoboImportedSubmission.objects.create(
        registration_data_import=registration_data_import,
        kobo_submission_uuid=submission_uuid,
        kobo_asset_id="test",
        kobo_submission_time=timezone.now(),
        imported_household=imported_household,
    )


@pytest.fixture
def submissions(business_area: BusinessArea) -> None:
    _make_submission(business_area, RegistrationDataImport.MERGED)
    _make_submission(business_area, RegistrationDataImport.MERGED)
    _make_submission(business_area, RegistrationDataImport.IN_REVIEW)


def test_mark_submissions(business_area: BusinessArea, submissions: None) -> None:
    task = MarkSubmissions(business_area)
    task.execute()

    assert KoboImportedSubmission.objects.filter(amended=True).count() == 1
