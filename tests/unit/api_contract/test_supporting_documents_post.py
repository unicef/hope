from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import PostRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import PaymentPlanGroupFactory
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


@frozenfixture()
def payment_plan_group(request, db, program, superuser):
    return PaymentPlanGroupFactory(cycle=program.cycles.first(), created_by=superuser)


def test_create_supporting_document(superuser, business_area, program, role_assignment, payment_plan_group):
    recorder = PostRecorder(DATA_DIR, as_user=superuser)
    url = (
        f"/api/rest/business-areas/{business_area.slug}"
        f"/programs/{program.code}/payment-plan-groups/{payment_plan_group.pk}/supporting-documents/"
    )
    data = {
        "title": "Test Document",
        "file": SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
    }
    recorder.assertPOST(url, data)
