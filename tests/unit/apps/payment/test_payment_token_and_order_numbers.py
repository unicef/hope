from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.payment.validators import payment_token_and_order_number_validator
from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
    check_if_token_or_order_number_exists_per_program,
    generate_token_and_order_numbers,
)
from hope.models.country import Country
from hope.models.household import Household
from hope.models.payment import Payment
from hope.models.payment_plan import PaymentPlan


class TestPaymentTokenAndOrderNumbers(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = create_afghanistan()
        country_origin = Country.objects.filter(iso_code2="UA").first()

        for n in range(1, 3):
            create_household(
                {"size": n, "address": "Lorem Ipsum", "country_origin": country_origin},
            )
        program = ProgramFactory(business_area=business_area)

        cls.payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            status=PaymentPlan.Status.ACCEPTED,
            business_area=business_area,
        )
        program.households.set(Household.objects.all())
        for household in program.households.all():
            PaymentFactory(
                parent=cls.payment_plan,
                household=household,
                program=program,
                currency="PLN",
            )

    def test_payments_created_payments(self) -> None:
        assert self.payment_plan.eligible_payments.count() == 2

        for payment in self.payment_plan.eligible_payments.all():
            assert payment.order_number is None
            assert payment.token_number is None

    def test_generate_token_and_order_numbers_for_payments(self) -> None:
        service = XlsxPaymentPlanExportPerFspService(self.payment_plan, None)
        service.generate_token_and_order_numbers(self.payment_plan.eligible_payments.all(), self.payment_plan.program)
        payment = self.payment_plan.eligible_payments.first()
        assert len(str(payment.order_number)) == 9
        assert len(str(payment.token_number)) == 7

    def test_validation_token_must_not_has_the_same_digit_more_than_three_times(self) -> None:
        with pytest.raises(ValidationError):
            payment_token_and_order_number_validator(1111111)

    def test_validation_save_payment_with_exists_token_or_order_number(self) -> None:
        payment_1 = Payment.objects.first()
        payment_2 = Payment.objects.last()

        token_number = 1112223
        order_number = 111222333

        payment_1.token_number = token_number
        payment_1.order_number = order_number
        payment_1.save()

        payment_2.token_number = token_number
        payment_2.order_number = order_number
        with pytest.raises(IntegrityError):
            payment_2.save(update_fields=["order_number", "token_number"])
