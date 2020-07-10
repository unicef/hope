import factory
from factory import fuzzy
from pytz import utc

from core.models import BusinessArea
from household.fixtures import HouseholdFactory
from payment.models import (
    PaymentRecord,
    ServiceProvider,
    CashPlanPaymentVerification,
    PaymentVerification,
)
from program.fixtures import CashPlanFactory
from program.models import CashPlan
from targeting.fixtures import TargetPopulationFactory


class ServiceProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    business_area = factory.LazyAttribute(
        lambda o: BusinessArea.objects.first()
    )
    ca_id = factory.Faker("uuid4")
    full_name = factory.Faker("company")
    short_name = factory.LazyAttribute(lambda o: o.full_name[0:3])
    country = factory.Faker("country_code")
    vision_id = factory.Faker("uuid4")


class PaymentRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    business_area = factory.LazyAttribute(
        lambda o: BusinessArea.objects.first()
    )
    status = fuzzy.FuzzyChoice(
        PaymentRecord.STATUS_CHOICE, getter=lambda c: c[0],
    )
    full_name = factory.Faker("name")
    status_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    # ca_id = factory.Faker("uuid4")
    # ca_hash_id = factory.Faker("uuid4")
    cash_plan = factory.SubFactory(CashPlanFactory)
    household = factory.SubFactory(HouseholdFactory)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 7)
    distribution_modality = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
    entitlement_card_number = factory.Faker("ssn")
    entitlement_card_status = fuzzy.FuzzyChoice(
        PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE, getter=lambda c: c[0],
    )
    entitlement_card_issue_date = factory.Faker(
        "date_time_this_decade", before_now=True, after_now=False, tzinfo=utc,
    )
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE, getter=lambda c: c[0],
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivered_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivery_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    service_provider = factory.SubFactory(ServiceProviderFactory)


class CashPlanPaymentVerificationFactory(factory.DjangoModelFactory):
    status = fuzzy.FuzzyChoice(
        CashPlanPaymentVerification.STATUS_CHOICES, getter=lambda c: c[0],
    )
    sampling = fuzzy.FuzzyChoice(
        CashPlanPaymentVerification.SAMPLING_CHOICES, getter=lambda c: c[0],
    )
    verification_method = fuzzy.FuzzyChoice(
        CashPlanPaymentVerification.VERIFICATION_METHOD_CHOICES,
        getter=lambda c: c[0],
    )
    cash_plan = factory.Iterator(CashPlan.objects.all())
    sample_size = fuzzy.FuzzyInteger(0, 100)
    responded_count = fuzzy.FuzzyInteger(20, 90)
    received_count = fuzzy.FuzzyInteger(30, 70)
    not_received_count = fuzzy.FuzzyInteger(0, 10)
    received_with_problems_count = fuzzy.FuzzyInteger(0, 10)

    class Meta:
        model = CashPlanPaymentVerification


class PaymentVerificationFactory(factory.DjangoModelFactory):
    cash_plan_payment_verification = factory.Iterator(
        CashPlanPaymentVerification.objects.all()
    )
    payment_record = factory.LazyAttribute(
        lambda o: PaymentRecord.objects.filter(
                cash_plan=o.cash_plan_payment_verification.cash_plan
            ).order_by("?").first()
    )
    status = fuzzy.FuzzyChoice(
        PaymentVerification.STATUS_CHOICES, getter=lambda c: c[0],
    )
    status_date = factory.Faker(
        "date_this_year", before_today=True, after_today=False
    )

    class Meta:
        model = PaymentVerification
