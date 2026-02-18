from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import PostRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory

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
def payment_plan(request, db, business_area, program, superuser):
    cycle = ProgramCycleFactory(program=program)
    return PaymentPlanFactory(business_area=business_area, program_cycle=cycle, created_by=superuser)


def test_create_supporting_document(superuser, business_area, program, role_assignment, payment_plan):
    recorder = PostRecorder(DATA_DIR, as_user=superuser)
    url = (
        f"/api/rest/business-areas/{business_area.slug}"
        f"/programs/{program.slug}/payment-plans/{payment_plan.pk}/supporting-documents/"
    )
    data = {
        "title": "Test Document",
        "file": SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
    }
    recorder.assertPOST(url, data)
