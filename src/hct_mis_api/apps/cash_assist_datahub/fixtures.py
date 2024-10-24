from datetime import timedelta
from random import randint

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    PaymentRecord,
    Programme,
    ServiceProvider,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment import models as payment_models
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.program import models as program_models
from hct_mis_api.apps.targeting.models import TargetPopulation


class ServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first().cash_assist_code)
    ca_id = factory.Faker("uuid4")
    full_name = factory.Faker("company")
    short_name = factory.LazyAttribute(lambda o: o.full_name[0:3])
    country = factory.Faker("country_code")
    vision_id = factory.Faker("uuid4")


class PaymentRecordFactory(DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first().cash_assist_code)
    status = fuzzy.FuzzyChoice(
        payment_models.PaymentRecord.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    full_name = factory.Faker("name")
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    ca_id = factory.Faker("uuid4")
    ca_hash_id = factory.Faker("uuid4")
    household_mis_id = factory.LazyAttribute(lambda o: Household.objects.order_by("?").first().id)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 7)
    distribution_modality = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    target_population_mis_id = factory.LazyAttribute(lambda o: TargetPopulation.objects.order_by("?").first().id)
    entitlement_card_number = factory.Faker("ssn")
    entitlement_card_status = fuzzy.FuzzyChoice(
        payment_models.PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    entitlement_card_issue_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    delivery_type = fuzzy.FuzzyChoice(
        DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES,
        getter=lambda c: c[0],
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivered_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivery_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    service_provider_ca_id = factory.LazyAttribute(lambda o: ServiceProvider.objects.order_by("?").first().ca_id)


class CashPlanFactory(DjangoModelFactory):
    class Meta:
        model = CashPlan

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first().cash_assist_code)

    program_mis_id = factory.LazyAttribute(lambda o: program_models.Program.objects.order_by("?").first().id)
    cash_plan_id = factory.Faker("uuid4")
    cash_plan_hash_id = factory.Faker("uuid4")
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    status = fuzzy.FuzzyChoice(
        CashPlan.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    name = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    distribution_level = "Registration Group"
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    dispersion_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    coverage_duration = factory.fuzzy.FuzzyInteger(1, 4)
    coverage_unit = factory.Faker(
        "random_element",
        elements=["Day(s)", "Week(s)", "Month(s)", "Year(s)"],
    )
    comments = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    delivery_type = fuzzy.FuzzyChoice(
        DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES,
        getter=lambda c: c[0],
    )
    assistance_measurement = factory.Faker("currency_name")
    assistance_through = factory.Faker("random_element", elements=["ING", "Bank of America", "mBank"])
    vision_id = factory.Faker("uuid4")
    funds_commitment = factory.fuzzy.FuzzyInteger(1000, 99999999)
    down_payment = factory.fuzzy.FuzzyInteger(1000, 99999999)
    validation_alerts_count = factory.fuzzy.FuzzyInteger(1, 3)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 4)
    total_persons_covered_revised = factory.fuzzy.FuzzyInteger(1, 4)

    total_entitled_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_entitled_quantity_revised = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_delivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)


class ProgrammeFactory(DjangoModelFactory):
    mis_id = None
    ca_id = factory.Faker("uuid4")
    ca_hash_id = factory.Faker("uuid4")

    class Meta:
        model = Programme
