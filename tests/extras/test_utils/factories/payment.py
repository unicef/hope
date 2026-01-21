"""Payment-related factories."""

from datetime import date, timedelta

from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from hope.models import (
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)


class PaymentPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlan

    status_date = factory.LazyFunction(timezone.now)
    status = PaymentPlan.Status.OPEN
    dispersion_start_date = factory.LazyFunction(date.today)
    dispersion_end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    status_date = factory.LazyFunction(timezone.now)
    currency = "PLN"


class PaymentVerificationSummaryFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerificationSummary


class PaymentVerificationPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerificationPlan

    verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
    sampling = "FULL_LIST"


class PaymentVerificationFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerification
