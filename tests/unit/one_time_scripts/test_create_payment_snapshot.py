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
from hct_mis_api.apps.payment.models import DeliveryMechanism, PaymentHouseholdSnapshot
from hct_mis_api.apps.utils.models import MergeStatusModel
from hct_mis_api.one_time_scripts.create_payment_snapshot import create_payment_snapshot


class TestMigratePaymentSnapShot(TestCase):
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
            )
            cls.p2 = PaymentFactory(
                parent=cls.pp,
                conflicted=False,
                household=cls.hh2,
                head_of_household=cls.hoh2,
            )

    def test_create_payment_snapshot(self) -> None:
        self.assertEqual(PaymentHouseholdSnapshot.objects.all().count(), 0)

        create_payment_snapshot()

        self.assertEqual(PaymentHouseholdSnapshot.objects.all().count(), 2)
