import pytest

from extras.test_utils.factories import DocumentTypeFactory, PendingDocumentFactory
from hope.apps.household.views import get_individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def tax_id_document_type(db):
    return DocumentTypeFactory(key="tax_id")


@pytest.fixture
def pending_document(tax_id_document_type):
    return PendingDocumentFactory(
        document_number="TAX123",
        type=tax_id_document_type,
    )


def test_get_individual_returns_individual_for_single_document(pending_document):
    result = get_individual("TAX123", None)

    assert result == pending_document.individual
