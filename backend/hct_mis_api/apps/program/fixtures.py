import random
import string
from datetime import datetime, timedelta
from random import randint
from typing import Any

from django.utils.timezone import utc

import factory
from dateutil.relativedelta import relativedelta
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import Program, ProgramCycle

fake = Faker()


class ProgramCycleFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCycle
        django_get_or_create = ("program", "title")

    status = ProgramCycle.ACTIVE
    start_date = factory.LazyAttribute(
        lambda o: (
            o.program.cycles.latest("start_date").end_date + timedelta(days=1)
            if o.program.cycles.exists()
            else fake.date_time_this_decade(before_now=True, after_now=True, tzinfo=utc).date()
        )
    )

    end_date = factory.LazyAttribute(lambda o: (o.start_date + timedelta(days=randint(60, 1000))))
    title = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    program = factory.SubFactory("program.fixtures.ProgramFactory")


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ("programme_code", "business_area")

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    name = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    status = fuzzy.FuzzyChoice(
        Program.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    start_date = factory.Faker(
        "date_this_decade",
        before_today=False,
        after_today=True,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True,
        ext_word_list=None,
    )
    budget = factory.fuzzy.FuzzyDecimal(1000000.0, 900000000.0)
    frequency_of_payments = fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE,
        getter=lambda c: c[0],
    )
    sector = fuzzy.FuzzyChoice(
        Program.SECTOR_CHOICE,
        getter=lambda c: c[0],
    )
    scope = fuzzy.FuzzyChoice(
        Program.SCOPE_CHOICE,
        getter=lambda c: c[0],
    )
    cash_plus = fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)
    administrative_areas_of_implementation = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    programme_code = factory.LazyAttribute(
        lambda o: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    )

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return
        ProgramCycleFactory(program=self, **kwargs)


def get_program_with_dct_type_and_name(
    dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE, **kwargs: dict
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        **kwargs,
    )
    return program
