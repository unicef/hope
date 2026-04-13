from datetime import datetime
import uuid

from django.utils import timezone
import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.apps.registration_data.validators import KoboProjectImportDataInstanceValidator
from hope.models import KoboImportedSubmission

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


def test_build_saved_submissions_lookup_groups_by_uuid(business_area):
    asset_id = "test_asset_123"
    sub_uuid = uuid.uuid4()
    time_1 = timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0))
    time_2 = timezone.make_aware(datetime(2024, 1, 2, 12, 0, 0))

    KoboImportedSubmission.objects.create(
        kobo_submission_uuid=sub_uuid,
        kobo_asset_id=asset_id,
        kobo_submission_time=time_1,
    )
    KoboImportedSubmission.objects.create(
        kobo_submission_uuid=sub_uuid,
        kobo_asset_id=asset_id,
        kobo_submission_time=time_2,
    )

    validator = KoboProjectImportDataInstanceValidator.__new__(KoboProjectImportDataInstanceValidator)
    reduced_submissions = [{"_xform_id_string": asset_id}]

    result = validator._build_saved_submissions_lookup(reduced_submissions, business_area)

    assert str(sub_uuid) in result
    assert len(result[str(sub_uuid)]) == 2
    assert time_1.isoformat() in result[str(sub_uuid)]
    assert time_2.isoformat() in result[str(sub_uuid)]
