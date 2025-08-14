from datetime import datetime

from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from freezegun import freeze_time

from hope.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hope.apps.payment.models import (
    AccountType,
    DeliveryMechanism,
    FinancialServiceProvider,
)
from hope.apps.payment.services import payment_household_snapshot_service
from hope.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hope.apps.utils.models import MergeStatusModel


class TestBuildSnapshot(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.fsp = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            vision_vendor_number=123456789,
        )
        generate_delivery_mechanisms()
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        cls.dm_mobile_money = DeliveryMechanism.objects.get(code="mobile_money")

        with freeze_time("2020-10-10"):
            program = RealProgramFactory()
            program_cycle = program.cycles.first()
            cls.pp = PaymentPlanFactory(
                program_cycle=program_cycle,
                is_follow_up=False,
            )
            cls.pp.unicef_id = "PP-01"
            cls.pp.save()

            cls.hoh1 = IndividualFactory(household=None)
            cls.hoh2 = IndividualFactory(household=None)
            cls.hh1 = HouseholdFactory(head_of_household=cls.hoh1)
            cls.hh2 = HouseholdFactory(head_of_household=cls.hoh2)
            cls.primary_role = IndividualRoleInHousehold.objects.create(
                household=cls.hh1,
                individual=cls.hoh1,
                role=ROLE_PRIMARY,
                rdi_merge_status=MergeStatusModel.MERGED,
            )
            cls.hoh1.household = cls.hh1
            cls.hoh1.save()
            AccountFactory(
                individual=cls.hoh1,
                account_type=AccountType.objects.get(key="bank"),
                data={
                    "number": "123",
                    "expiry_date": "2022-01-01",
                    "name_of_cardholder": "Marek",
                },
            )
            cls.p1 = PaymentFactory(
                parent=cls.pp,
                conflicted=False,
                household=cls.hh1,
                head_of_household=cls.hoh1,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                currency="PLN",
                financial_service_provider=cls.fsp,
                delivery_type=cls.dm_atm_card,
            )
            cls.p2 = PaymentFactory(
                parent=cls.pp,
                conflicted=False,
                household=cls.hh2,
                head_of_household=cls.hoh2,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                currency="PLN",
                financial_service_provider=cls.fsp,
                delivery_type=cls.dm_atm_card,
            )

    def test_build_snapshot(self) -> None:
        create_payment_plan_snapshot_data(self.pp)
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertIsNotNone(self.p1.household_snapshot)
        self.assertIsNotNone(self.p2.household_snapshot)
        self.assertEqual(str(self.p1.household_snapshot.snapshot_data["id"]), str(self.hh1.id))
        self.assertEqual(str(self.p2.household_snapshot.snapshot_data["id"]), str(self.hh2.id))
        self.assertEqual(len(self.p1.household_snapshot.snapshot_data["individuals"]), self.hh1.individuals.count())
        self.assertEqual(len(self.p2.household_snapshot.snapshot_data["individuals"]), self.hh2.individuals.count())
        self.assertIsNotNone(self.p1.household_snapshot.snapshot_data["primary_collector"])
        self.assertEqual(
            self.p1.household_snapshot.snapshot_data["primary_collector"].get("account_data", {}),
            {
                "expiry_date": "2022-01-01",
                "number": "123",
                "name_of_cardholder": "Marek",
            },
        )

    def test_batching(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()
        pp = PaymentPlanFactory(
            program_cycle=program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
        )
        pp.unicef_id = "PP-02"
        pp.save()
        number_of_payments = 20
        payment_household_snapshot_service.page_size = 2
        for _ in range(number_of_payments):
            hoh1 = IndividualFactory(household=None)
            hh1 = HouseholdFactory(head_of_household=hoh1)
            PaymentFactory(
                parent=pp,
                conflicted=False,
                household=hh1,
                head_of_household=hoh1,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                financial_service_provider=None,
                currency="PLN",
            )
        self.assertEqual(pp.payment_items.count(), number_of_payments)
        create_payment_plan_snapshot_data(pp)
        self.assertEqual(pp.payment_items.filter(household_snapshot__isnull=False).count(), number_of_payments)
