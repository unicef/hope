from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from freezegun import freeze_time

from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
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
                program_cycle=program_cycle,
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
            AccountFactory(
                individual=cls.hoh1,
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
