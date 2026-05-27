import pytest
from rest_framework.exceptions import NotFound

from hope.apps.household.views import get_individual

pytestmark = pytest.mark.django_db


def test_get_individual_raises_not_found_when_no_document_matches_tax_id():
    with pytest.raises(NotFound, match="Document with given tax_id: NONEXISTENT-TAX-ID not found"):
        get_individual(tax_id="NONEXISTENT-TAX-ID", business_area_code=None)


def test_get_individual_raises_not_found_when_no_document_matches_tax_id_with_business_area_code():
    with pytest.raises(NotFound, match="Document with given tax_id: MISSING-TAX not found"):
        get_individual(tax_id="MISSING-TAX", business_area_code="afghanistan")
