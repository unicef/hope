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

    @classmethod
    def _create(cls, model_class: type, *args: Any, **kwargs: Any) -> Program:
        desired_status = kwargs.get("status", Program.ACTIVE)
        if desired_status == Program.ACTIVE:
            kwargs["status"] = Program.DRAFT
        obj = super()._create(model_class, *args, **kwargs)
        if desired_status == Program.ACTIVE:
            obj.payment_plan_purposes.add(PaymentPlanPurposeFactory(business_area=obj.business_area))
            obj.status = Program.ACTIVE
            obj.save()
        return obj


class ProgramCycleFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCycle

    program = factory.SubFactory(ProgramFactory)
    title = factory.Sequence(lambda n: f"Programme Cycle {n}")
    start_date = factory.LazyFunction(date.today)
    status = ProgramCycle.ACTIVE
