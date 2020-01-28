from datetime import timedelta
from random import randint

import factory
from factory import fuzzy
from pytz import utc

from household.fixtures import HouseholdFactory
from payment.models import PaymentRecord
from program.fixtures import CashPlanFactory


class PaymentRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    start_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=randint(60, 1000))
    )
    cash_assist_id = factory.Faker("uuid4")
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE, getter=lambda c: c[0],
    )
    cash_plan = factory.SubFactory(CashPlanFactory)
    household = factory.SubFactory(HouseholdFactory)
