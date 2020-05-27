from datetime import timedelta, datetime
from random import randint

import factory
from factory import fuzzy
from pytz import utc

from account.fixtures import UserFactory
from core.fixtures import AdminAreaFactory
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
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=randint(60, 1000))
    )
    description = factory.Faker(
        "sentence", nb_words=10, variable_nb_words=True, ext_word_list=None,
    )
    program_ca_id = factory.Faker("uuid4")
    locations = factory.SubFactory(AdminAreaFactory)
    budget = factory.fuzzy.FuzzyDecimal(1000000.0, 900000000.0)
    frequency_of_payments = fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE, getter=lambda c: c[0],
    )
    sector = fuzzy.FuzzyChoice(Program.SECTOR_CHOICE, getter=lambda c: c[0],)
    scope = fuzzy.FuzzyChoice(Program.SCOPE_CHOICE, getter=lambda c: c[0],)
    cash_plus = fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)
    administrative_areas_of_implementation = factory.Faker(
        "sentence", nb_words=3, variable_nb_words=True, ext_word_list=None,
    )

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            self.locations.add(AdminAreaFactory())

        if extracted:
            for location in extracted:
                self.locations.add(location)


class CashPlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = CashPlan

    program = factory.SubFactory(ProgramFactory)
    ca_id = factory.Faker("uuid4")
    ca_hash_id = factory.Faker("uuid4")
    status_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    status = fuzzy.FuzzyChoice(CashPlan.STATUS_CHOICE, getter=lambda c: c[0],)
    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    distribution_level = "Registration Group"
    start_date = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True, tzinfo=utc,
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=randint(60, 1000))
    )
    dispersion_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=randint(60, 1000))
    )
    coverage_duration = factory.fuzzy.FuzzyInteger(1, 4)
    coverage_unit = factory.Faker(
        "random_element", elements=["Day(s)", "Week(s)", "Month(s)", "Year(s)"],
    )
    comments = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    delivery_type = factory.Faker(
        "random_element", elements=["Deposit to Card", "Transfer", "Cash"]
    )
    assistance_measurement = factory.Faker("currency_name")
    assistance_through = factory.Faker(
        "random_element", elements=["ING", "Bank of America", "mBank"]
    )
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
