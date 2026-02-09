from pathlib import Path
from unittest.mock import patch

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import PostRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def business_area(request, db):
    return BusinessAreaFactory()


@frozenfixture()
def program(request, db, business_area):
    return ProgramFactory(business_area=business_area)


@frozenfixture()
def role(request, db):
    from hope.apps.account.permissions import Permissions

    return RoleFactory(permissions=[p.value for p in Permissions])


@frozenfixture()
def role_assignment(request, db, superuser, business_area, role):
    return RoleAssignmentFactory(user=superuser, business_area=business_area, role=role)


@patch("hope.apps.registration_datahub.celery_tasks.pull_kobo_submissions_task.delay")
def test_save_kobo_import_data(mock_delay, superuser, business_area, program, role_assignment):
    recorder = PostRecorder(DATA_DIR, as_user=superuser)
    url = (
        f"/api/rest/business-areas/{business_area.slug}"
        f"/programs/{program.slug}/kobo-import-data-upload/save-kobo-import-data/"
    )
    data = {
        "uid": "kobo_asset_abc",
        "only_active_submissions": True,
        "pull_pictures": False,
    }
    recorder.assertPOST(url, data)
