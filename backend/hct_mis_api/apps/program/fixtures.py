from datetime import timedelta
from random import randint

import factory
from factory import fuzzy
from pytz import utc

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.program.models import Program


class ProgramFactory(factory.DjangoModelFactory):
    class Meta:
        model = Program

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
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True,
        ext_word_list=None,
    )
    locations = factory.SubFactory(AreaFactory)
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
    individual_data_needed = fuzzy.FuzzyChoice((True, False))

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            self.locations.add(AreaFactory())

        if extracted:
            for location in extracted:
                self.locations.add(location)
