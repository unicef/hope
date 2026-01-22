"""Payment-related factories."""

from datetime import date, timedelta

from django.utils import timezone
import factory
from factory.django import DjangoModelFactory

from extras.test_utils.factories import UserFactory
from hope.models import (
    Account,
    AccountType,
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)

from .program import ProgramCycleFactory


class PaymentPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlan

    status_date = factory.LazyFunction(timezone.now)
    status = PaymentPlan.Status.OPEN
    dispersion_start_date = factory.LazyFunction(date.today)
    dispersion_end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    program_cycle = factory.SubFactory(ProgramCycleFactory)
    created_by = factory.SubFactory(UserFactory)


class AccountTypeFactory(DjangoModelFactory):
    class Meta:
        model = AccountType

    key = factory.Sequence(lambda n: f"account_type_{n}")
    label = factory.Sequence(lambda n: f"Account Type {n}")
    unique_fields = []


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account

    number = factory.Sequence(lambda n: f"ACC-{n}")
    data = factory.LazyFunction(dict)


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


class DeliveryMechanismFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryMechanism

    code = factory.Sequence(lambda n: f"DM{n:04d}")
    name = factory.Sequence(lambda n: f"Delivery Mechanism {n}")
    payment_gateway_id = factory.Sequence(lambda n: f"dm-{n}")


class FinancialServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProvider

    name = factory.Sequence(lambda n: f"FSP {n}")
    vision_vendor_number = factory.Sequence(lambda n: f"VEN{n:04d}")
    communication_channel = FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX

    @factory.post_generation
    def delivery_mechanisms(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for delivery_mechanism in extracted:
                self.delivery_mechanisms.add(delivery_mechanism)


class FinancialServiceProviderXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProviderXlsxTemplate

    name = factory.Sequence(lambda n: f"FSP Template {n}")
