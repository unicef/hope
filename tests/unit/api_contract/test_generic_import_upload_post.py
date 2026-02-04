from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
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


def test_upload_generic_import(superuser, business_area, program, role_assignment):
    recorder = PostRecorder(DATA_DIR, as_user=superuser)
    url = f"/api/rest/business-areas/{business_area.slug}/programs/{program.slug}/generic-import-upload/upload/"
    data = {
        "file": SimpleUploadedFile(
            "test.xlsx",
            b"PK\x03\x04fake",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }
    recorder.assertPOST(url, data)
