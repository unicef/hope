from datetime import timedelta, datetime

import factory
from factory import fuzzy
from pytz import utc

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from program.models import Program, CashPlan
from targeting.fixtures import TargetPopulationFactory


class ProgramFactory(factory.DjangoModelFactory):
    class Meta:
        model = Program

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    status = fuzzy.FuzzyChoice(Program.STATUS_CHOICE, getter=lambda c: c[0],)
    start_date = factory.Faker(
        "date_time_this_century", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.Faker(
        "date_time_this_century", before_now=False, after_now=True, tzinfo=utc,
    )
    description = factory.Faker(
        "sentence", nb_words=10, variable_nb_words=True, ext_word_list=None,
    )
    program_ca_id = factory.Faker("uuid4")
    location = factory.SubFactory(LocationFactory)
    budget = factory.fuzzy.FuzzyDecimal(1000000.0, 900000000.0)
    frequency_of_payments = fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE, getter=lambda c: c[0],
    )
    sector = fuzzy.FuzzyChoice(Program.SECTOR_CHOICE, getter=lambda c: c[0],)
    scope = fuzzy.FuzzyChoice(Program.SCOPE_CHOICE, getter=lambda c: c[0],)
    cash_plus = fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)


class CashPlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = CashPlan

    program = factory.SubFactory(ProgramFactory)
    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    start_date = factory.Faker(
        "date_time_this_century", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.Faker(
        "date_time_this_century", before_now=False, after_now=True, tzinfo=utc,
    )
    disbursement_date = factory.LazyAttribute(
        lambda o: o.end_date - timedelta(days=5)
    )
    number_of_households = factory.fuzzy.FuzzyInteger(100, 550)
    created_date = factory.LazyAttribute(
        lambda o: o.start_date - timedelta(days=5)
    )
    created_by = factory.SubFactory(UserFactory)
    coverage_duration = factory.fuzzy.FuzzyInteger(10, 30)
    coverage_units = factory.Faker(
        "random_element", elements=["Day(s)", "Week(s)", "Month(s)", "Year(s)"],
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
    cash_assist_id = factory.Faker("uuid4")
    distribution_modality = factory.Faker(
        "pystr_format", string_format="###-##",
    )
    fsp = factory.Faker("company")
    status = fuzzy.FuzzyChoice(CashPlan.STATUS_CHOICE, getter=lambda c: c[0],)
    currency = factory.Faker("currency_name")
    total_entitled_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_delivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    dispersion_date = fuzzy.FuzzyDate(
        start_date=datetime.now() + timedelta(days=30),
        end_date=datetime.now() + timedelta(days=365),
    )
