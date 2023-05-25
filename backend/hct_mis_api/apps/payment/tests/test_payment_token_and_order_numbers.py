from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.validators import payment_token_and_order_number_validator
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
    check_if_token_or_order_number_exists_per_program,
    generate_token_and_order_numbers,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentTokenAndOrderNumbers(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        business_area = create_afghanistan()
        country_origin = Country.objects.filter(iso_code2="UA").first()

        for n in range(1, 3):
            create_household(
                {"size": n, "address": "Lorem Ipsum", "country_origin": country_origin},
            )
        program = ProgramFactory(business_area=business_area)

        cls.payment_plan = PaymentPlanFactory(
            program=program, status=PaymentPlan.Status.ACCEPTED, business_area=business_area
        )
        program.households.set(Household.objects.all().values_list("id", flat=True))
        for household in program.households.all():
            PaymentFactory(
                parent=cls.payment_plan,
                household=household,
                program=program,
            )

    def test_payments_created_payments(self) -> None:
        assert self.payment_plan.eligible_payments.count() == 2

        for payment in self.payment_plan.eligible_payments.all():
            assert payment.order_number is None
            assert payment.token_number is None

    def test_generate_token_and_order_numbers_for_payments(self) -> None:
        for payment in self.payment_plan.eligible_payments.all():
            payment = generate_token_and_order_numbers(payment)

            assert len(str(payment.order_number)) == 9
            assert len(str(payment.token_number)) == 7

    def test_check_if_token_or_order_number_exists_per_program(self) -> None:
        payment = Payment.objects.first()
        payment.token_number = 1234567
        payment.order_number = 987654321
        payment.save(update_fields=["token_number", "order_number"])
        payment.refresh_from_db()
        assert check_if_token_or_order_number_exists_per_program(payment, "token_number", 1234567) is True
        assert check_if_token_or_order_number_exists_per_program(payment, "token_number", 7777777) is False
        assert check_if_token_or_order_number_exists_per_program(payment, "order_number", 987654321) is True
        assert check_if_token_or_order_number_exists_per_program(payment, "order_number", 123456789) is False

    def test_validation_token_must_not_has_the_same_digit_more_than_three_times(self) -> None:
        with self.assertRaises(ValidationError):
            payment_token_and_order_number_validator(1111111)

    def test_validation_save_payment_with_exists_token_or_order_number(self) -> None:
        payment_1 = Payment.objects.first()
        payment_2 = Payment.objects.last()

        token_number = 1112223
        order_number = 111222333

        payment_1.token_number = token_number
        payment_1.order_number = order_number
        payment_1.save()

        with self.assertRaises(IntegrityError):
            payment_2.token_number = token_number
            payment_2.save()

        with self.assertRaises(IntegrityError):
            payment_2.order_number = order_number
            payment_2.save()
