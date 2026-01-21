"""Program-related factories."""

from datetime import date, timedelta
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from hope.models import Program, ProgramCycle

from .core import BeneficiaryGroupFactory, DataCollectingTypeFactory


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program

    name = factory.Sequence(lambda n: f"Program {n}")
    status = Program.ACTIVE
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=365))
    budget = Decimal(1000000)
    frequency_of_payments = Program.ONE_OFF
    sector = Program.MULTI_PURPOSE
    cash_plus = False
    population_goal = 1000
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    beneficiary_group = factory.SubFactory(BeneficiaryGroupFactory)


class ProgramCycleFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCycle

    program = factory.SubFactory(ProgramFactory)
    start_date = factory.LazyFunction(date.today)
    status = ProgramCycle.ACTIVE
