from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.fixtures import (
    AccountFactory,
    PaymentFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import Account, AccountType, DeliveryMechanism
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    bulk_create_payment_snapshot_data,
)
from hct_mis_api.one_time_scripts.migrate_mobile_money_accounts import (
    migrate_mobile_money_accounts,
)


class TestMigrateMobileMoneyAccounts(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()
        cls.mobile_account_type = AccountType.objects.get(key="mobile")
        mobile_money_dm = DeliveryMechanism.objects.get(code="mobile_money")

        # collector with 2 payments, without account, phone_no match, expect to create 1 new active account
        cls.collector1 = IndividualFactory(household=None, phone_no="123")
        hh1 = HouseholdFactory(head_of_household=cls.collector1)
        IndividualRoleInHouseholdFactory(household=hh1, individual=cls.collector1, role=ROLE_PRIMARY)
        payment1a = PaymentFactory(
            currency="PLN", collector=cls.collector1, delivery_type=mobile_money_dm, household=hh1
        )
        payment1b = PaymentFactory(
            currency="PLN", collector=cls.collector1, delivery_type=mobile_money_dm, household=hh1
        )
        bulk_create_payment_snapshot_data([payment1a.id, payment1b.id])

        # collector with 1 payment, without account, phone_no doesn't match, expect to create 1 new inactive account
        cls.collector2 = IndividualFactory(household=None, phone_no="345")
        hh2 = HouseholdFactory(head_of_household=cls.collector2)
        IndividualRoleInHouseholdFactory(household=hh2, individual=cls.collector2, role=ROLE_PRIMARY)
        payment2 = PaymentFactory(
            currency="PLN", collector=cls.collector2, delivery_type=mobile_money_dm, household=hh2
        )
        bulk_create_payment_snapshot_data([payment2.id])
        cls.collector2.phone_no = "3456"
        cls.collector2.save()

        # collector with 1 payment, with account, no action
        cls.collector3 = IndividualFactory(household=None, phone_no="678")
        hh3 = HouseholdFactory(head_of_household=cls.collector3)
        IndividualRoleInHouseholdFactory(household=hh3, individual=cls.collector3, role=ROLE_PRIMARY)
        AccountFactory(
            individual=cls.collector3,
            account_type=cls.mobile_account_type,
            number="678",
            data={"number": "678", "abc": 1},
        )
        payment3 = PaymentFactory(
            currency="PLN", collector=cls.collector3, delivery_type=mobile_money_dm, household=hh3
        )
        bulk_create_payment_snapshot_data([payment3.id])

    def test_migrate_mobile_money_accounts(self) -> None:
        migrate_mobile_money_accounts()
        self.assertEqual(Account.objects.count(), 3)
        account1 = self.collector1.accounts.first()
        self.assertEqual(account1.account_type, self.mobile_account_type)
        self.assertEqual(account1.number, "123")
        self.assertEqual(account1.active, True)
        self.assertEqual(account1.data, {"number": "123"})
        self.assertEqual(account1.rdi_merge_status, "MERGED")

        account2 = self.collector2.accounts.first()
        self.assertEqual(account2.account_type, self.mobile_account_type)
        self.assertEqual(account2.number, "345")
        self.assertEqual(account2.active, False)
        self.assertEqual(account2.data, {"number": "345"})
        self.assertEqual(account2.rdi_merge_status, "MERGED")

        account3 = self.collector3.accounts.first()
        self.assertEqual(account3.account_type, self.mobile_account_type)
        self.assertEqual(account3.number, "678")
        self.assertEqual(account3.active, True)
        self.assertEqual(account3.data, {"number": "678", "abc": 1})
        self.assertEqual(account3.rdi_merge_status, "MERGED")
