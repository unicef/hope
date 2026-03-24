import pytest

from hope.models import FinancialInstitution

pytestmark = pytest.mark.django_db


@pytest.fixture
def generic_financial_institutions():
    return [
        FinancialInstitution.objects.create(
            name="Generic Telco Company",
            type=FinancialInstitution.FinancialInstitutionType.TELCO,
        ),
        FinancialInstitution.objects.create(
            name="Generic Bank",
            type=FinancialInstitution.FinancialInstitutionType.BANK,
        ),
        FinancialInstitution.objects.create(
            name="IBAN Provider Bank",
            type=FinancialInstitution.FinancialInstitutionType.BANK,
        ),
    ]


def test_get_generic_one(generic_financial_institutions):
    cases = [
        ("mobile", True, "Generic Telco Company"),
        ("card", True, "Generic Bank"),
        ("xxx", True, "Generic Bank"),
        ("bank", True, "IBAN Provider Bank"),
        ("bank", False, "Generic Bank"),
    ]
    for account_type, is_valid_iban, expected_fi_name in cases:
        assert FinancialInstitution.get_generic_one(account_type, is_valid_iban).name == expected_fi_name
