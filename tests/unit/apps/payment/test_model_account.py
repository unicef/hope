from unittest import mock

from django.db import transaction
from django.db.utils import IntegrityError
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import AccountFactory, AccountTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.household.const import LOT_DIFFICULTY
from hope.models import Account, MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def individual(business_area):
    return IndividualFactory(household=None, business_area=business_area)


@pytest.fixture
def account_type_bank(business_area):
    return AccountTypeFactory(
        key="bank",
        label="Bank",
        unique_fields=[
            "number",
            "seeing_disability",
            "data_field",
        ],
        payment_gateway_id="123",
    )


@pytest.fixture
def account(individual):
    return AccountFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)


@pytest.fixture
def household_with_two_individuals(business_area):
    program = ProgramFactory(business_area=business_area)
    individual_1 = IndividualFactory(household=None, program=program, business_area=business_area)
    individual_2 = IndividualFactory(household=None, program=program, business_area=business_area)
    household = HouseholdFactory(head_of_household=individual_1, program=program)
    individual_1.household = household
    individual_1.save()
    individual_2.household = household
    individual_2.save()
    return household, individual_1, individual_2


def test_account_str(account):
    assert str(account) == f"{account.individual} - {account.account_type}"


def test_validate_uniqueness(account, monkeypatch):
    update_unique_field_mock = mock.Mock()
    monkeypatch.setattr(Account, "update_unique_field", update_unique_field_mock)
    Account.validate_uniqueness(Account.objects.all())
    update_unique_field_mock.assert_called_once()


def test_update_unique_field_empty_unique_fields_resets_flags(account):
    account.unique_key = "abc"
    account.is_unique = False
    account.save(update_fields=["unique_key", "is_unique"])

    account.update_unique_field()
    account.refresh_from_db()
    assert account.unique_key is None
    assert account.is_unique is True


@pytest.mark.parametrize(
    ("desc", "active", "is_unique", "unique_key", "should_raise"),
    [
        ("Inactive, should pass", False, True, "wallet-1", False),
        ("is_unique=False, should pass", True, False, "wallet-1", False),
        ("Both False, should pass", False, False, "wallet-1", False),
        ("Null key, should pass", True, True, None, False),
        ("Different key, should pass", True, True, "wallet-2", False),
        ("Duplicate violating row", True, True, "wallet-1", True),
    ],
)
def test_unique_active_wallet_constraint(individual, desc, active, is_unique, unique_key, should_raise):
    AccountFactory(
        individual=individual,
        unique_key="wallet-1",
        active=True,
        is_unique=True,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    kwargs = {
        "individual": individual,
        "unique_key": unique_key,
        "active": active,
        "is_unique": is_unique,
        "rdi_merge_status": MergeStatusModel.MERGED,
    }
    if should_raise:
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                AccountFactory(**kwargs)
    else:
        AccountFactory(**kwargs)


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (None, False),
        ("", False),
        (" ", False),
        ("1", False),
        (123333, False),
        ("PL", False),
        ("PL00", False),
        ("PL00ABC", False),
        ("PL00123456789012345678901234X", False),
        ("PL00 1234 5678 9012 3456 7890 1234", True),
        ("pl00 1234 5678 9012 3456 7890 1234", True),
        ("DE89370400440532013000", True),
        ("GB82WEST12345698765432", True),
        ("NO9386011117947", True),
        ("NL91ABNA0417164300", True),
        ("FR1420041010050500013M02606", True),
        ("DE8937040044053201300", False),
        ("DE893704004405320130000", False),
        ("ZZ0012345678901234", True),
    ],
)
def test_is_valid_iban(number, expected):
    assert Account.is_valid_iban(number) == expected


def test_update_unique_fields(account_type_bank, household_with_two_individuals):
    _, ind, ind2 = household_with_two_individuals

    dmd_1 = AccountFactory(
        data={"data_field": "test"},
        individual=ind,
        account_type=account_type_bank,
        number="123",
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    dmd_1.individual.seeing_disability = LOT_DIFFICULTY
    dmd_1.individual.save()
    assert dmd_1.unique_key is None
    assert dmd_1.is_unique is True

    dmd_2 = AccountFactory(
        data={"data_field": "test2"},
        individual=ind2,
        account_type=account_type_bank,
        number="123",
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    dmd_2.individual.seeing_disability = LOT_DIFFICULTY
    dmd_2.individual.save()
    assert dmd_2.unique_key is None
    assert dmd_2.is_unique is True

    dmd_1.update_unique_field()
    dmd_2.update_unique_field()

    dmd_1.refresh_from_db()
    dmd_2.refresh_from_db()
    assert dmd_1.is_unique is True
    assert dmd_2.is_unique is True
    assert dmd_1.unique_key is not None
    assert dmd_2.unique_key is not None
    assert dmd_1.unique_key != dmd_2.unique_key


def test_update_unique_field_collision_sets_not_unique(household_with_two_individuals, account_type_bank):
    _, individual_1, individual_2 = household_with_two_individuals

    account_1 = AccountFactory(
        individual=individual_1,
        account_type=account_type_bank,
        number="123",
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    account_2 = AccountFactory(
        individual=individual_2,
        account_type=account_type_bank,
        number="123",
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    account_1.update_unique_field()
    account_2.update_unique_field()

    account_1.refresh_from_db()
    account_2.refresh_from_db()
    assert account_1.is_unique is True
    assert account_2.is_unique is False
    assert account_1.unique_key == account_2.unique_key
