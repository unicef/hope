"""Program-related factories."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import factory
from factory.django import DjangoModelFactory

from hope.models import Program, ProgramCycle

from .core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory, PaymentPlanPurposeFactory


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
    business_area = factory.SubFactory(BusinessAreaFactory)
    biometric_deduplication_enabled = False

    @factory.post_generation
    def payment_plan_purposes(self, create: bool, extracted: Any, **kwargs: Any) -> None:
        if not create:
            return
        if extracted is not None:
            self.payment_plan_purposes.set(extracted)
        else:
            self.payment_plan_purposes.add(PaymentPlanPurposeFactory())

    @factory.post_generation
    def cycle(self, create: bool, extracted: Any, **kwargs: Any) -> None:
        if not create or extracted is False:
            return
        ProgramCycleFactory(program=self, **kwargs)


class ProgramCycleFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCycle

    program = factory.SubFactory(ProgramFactory, cycle=False)
    title = factory.Sequence(lambda n: f"Programme Cycle {n}")
    start_date = factory.LazyFunction(date.today)
    status = ProgramCycle.ACTIVE
