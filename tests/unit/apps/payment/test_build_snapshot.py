from datetime import datetime

from django.test import TestCase

from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.payment.services import payment_household_snapshot_service
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.utils.models import MergeStatusModel


class TestBuildSnapshot(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")

        with freeze_time("2020-10-10"):
            program = RealProgramFactory()
            program_cycle = program.cycles.first()
            cls.pp = PaymentPlanFactory(
                program=program,
                program_cycle=program_cycle,
                dispersion_start_date=datetime(2020, 8, 10),
                dispersion_end_date=datetime(2020, 12, 10),
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
            DeliveryMechanismDataFactory(
                individual=cls.hoh1,
                delivery_mechanism=cls.dm_atm_card,
                data={
                    "card_number__atm_card": "123",
                    "card_expiry_date__atm_card": "2022-01-01",
                    "name_of_cardholder__atm_card": "Marek",
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
            self.p1.household_snapshot.snapshot_data["primary_collector"].get("delivery_mechanisms_data", {}),
            {
                "atm_card": {
                    "card_expiry_date__atm_card": "2022-01-01",
                    "card_number__atm_card": "123",
                    "full_name": self.hoh1.full_name,
                    "name_of_cardholder__atm_card": "Marek",
                }
            },
        )

    def test_batching(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()
        pp = PaymentPlanFactory(
            program=program,
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
