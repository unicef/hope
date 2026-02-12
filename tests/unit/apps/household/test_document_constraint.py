from django.db import IntegrityError
import pytest

from extras.test_utils.factories import CountryFactory, DocumentTypeFactory, HouseholdFactory, ProgramFactory
from hope.models import Document
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def programs():
    return ProgramFactory.create_batch(2)


@pytest.fixture
def household(programs):
    program = programs[0]
    return HouseholdFactory(program=program, business_area=program.business_area)


@pytest.fixture
def document_data(household):
    country = CountryFactory(iso_code3="AFG")
    document_type = DocumentTypeFactory()
    return {
        "document_number": "test",
        "type": document_type,
        "individual": household.head_of_household,
        "country": country,
        "status": Document.STATUS_VALID,
        "rdi_merge_status": MergeStatusModel.MERGED,
    }


def test_allow_create_the_same_document_for_different_program(programs, document_data) -> None:
    Document.objects.create(program=programs[0], **document_data)
    Document.objects.create(program=programs[1], **document_data)


def test_disallow_create_the_same_document_for_the_same_program(programs, document_data) -> None:
    Document.objects.create(program=programs[0], **document_data)
    with pytest.raises(IntegrityError):
        Document.objects.create(program=programs[0], **document_data)
