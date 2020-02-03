from datetime import timedelta
from random import randint, sample

import factory
from factory import fuzzy
from pytz import utc

from household.fixtures import HouseholdFactory
from payment.models import (
    PaymentRecord,
    PaymentEntitlement,
    VerificationProcess,
    PaymentRecordVerification,
)
from program.fixtures import CashPlanFactory
from targeting.fixtures import TargetPopulationFactory


class PaymentEntitlementFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentEntitlement

    delivery_type = fuzzy.FuzzyChoice(
        PaymentEntitlement.DELIVERY_TYPE_CHOICE, getter=lambda c: c[0],
    )
    entitlement_quantity = factory.fuzzy.FuzzyInteger(90, 100)
    delivered_quantity = factory.LazyAttribute(
        lambda o: o.entitlement_quantity - randint(10, 80)
    )
    entitlement_card_issue_date = factory.Faker(
        "date_between", start_date="+1y", end_date="+4y"
    )
    entitlement_card_number = factory.Faker("credit_card_number")
    currency = factory.Faker("currency_name")
    delivery_date = factory.Faker(
        "future_datetime", end_date="+30d", tzinfo=utc
    )
    transaction_reference_id = factory.Faker("itin")
    fsp = factory.Faker("company")

class PaymentRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    status = fuzzy.FuzzyChoice(
        PaymentRecord.STATUS_CHOICE, getter=lambda c: c[0],
    )
    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    status_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    cash_assist_id = factory.Faker("uuid4")
    cash_plan = factory.SubFactory(CashPlanFactory)
    household = factory.SubFactory(HouseholdFactory)
    head_of_household = factory.Faker("name")
    total_person_covered = factory.fuzzy.FuzzyInteger(1, 7)
    distribution_modality = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
    entitlement = factory.SubFactory(PaymentEntitlementFactory)

class VerificationProcessFactory(factory.DjangoModelFactory):
    class Meta:
        model = VerificationProcess

    payment_records_to_verify = factory.fuzzy.FuzzyInteger(400, 1000)
    verification_type = fuzzy.FuzzyChoice(
        VerificationProcess.VERIFICATION_TYPE_CHOICE, getter=lambda c: c[0],
    )
    status = fuzzy.FuzzyChoice(
        VerificationProcess.STATUS_CHOICE, getter=lambda c: c[0],
    )


class PaymentRecordVerificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecordVerification
        exclude = ("integers_list",)

    integers_list = sample(range(randint(50, 200), randint(300, 900)), 5)

    start_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=randint(60, 1000))
    )
    sample_size = factory.LazyAttribute(lambda o: sum(o.integers_list))
    responded = factory.LazyAttribute(lambda o: o.integers_list[0])
    received = factory.LazyAttribute(lambda o: o.integers_list[1])
    not_received = factory.LazyAttribute(lambda o: o.integers_list[2])
    received_correct_amount = factory.LazyAttribute(
        lambda o: o.integers_list[3]
    )
    received_wrong_amount = factory.LazyAttribute(lambda o: o.integers_list[4])
    verification_process = factory.SubFactory(VerificationProcessFactory)
