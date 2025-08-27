from datetime import datetime, timedelta
import random
from random import randint
import string
from typing import Any

from dateutil.relativedelta import relativedelta
import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from extras.test_utils.factories.core import DataCollectingTypeFactory
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.program.models import BeneficiaryGroup, Program, ProgramCycle

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
            else (
                datetime.fromisoformat(o.program.start_date)
                if type(o.program.start_date) is str
                else o.program.start_date
            )
        )
    )

    end_date = factory.LazyAttribute(lambda o: (o.start_date + timedelta(days=randint(60, 1000))))
    title = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    program = factory.SubFactory("extras.test_utils.factories.program.ProgramFactory")


class BeneficiaryGroupFactory(DjangoModelFactory):
    name = "Household"
    group_label = factory.Faker("word")
    group_label_plural = factory.Faker("word")
    member_label = factory.Faker("word")
    member_label_plural = factory.Faker("word")
    master_detail = True

    class Meta:
        model = BeneficiaryGroup
        django_get_or_create = ("name",)


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ("name", "business_area", "programme_code")

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
    population_goal = factory.fuzzy.FuzzyInteger(50000, 600000)
    administrative_areas_of_implementation = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    programme_code = factory.LazyAttribute(lambda o: ProgramFactory.generate_programme_code(o))
    beneficiary_group = factory.LazyAttribute(
        lambda o: BeneficiaryGroupFactory(
            master_detail=bool(o.data_collecting_type.type != DataCollectingType.Type.SOCIAL),
            name=(
                factory.Faker("word") if o.data_collecting_type.type == DataCollectingType.Type.SOCIAL else "Household"
            ),
        )
    )

    @staticmethod
    def generate_programme_code(obj: Any) -> str:
        programme_code = "".join(random.choice(string.ascii_uppercase + string.digits + "-") for _ in range(4))
        if Program.objects.filter(business_area_id=obj.business_area.id, programme_code=programme_code).exists():
            return ProgramFactory.generate_programme_code(obj)
        return programme_code

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return
        ProgramCycleFactory(program=self, **kwargs)


def get_program_with_dct_type_and_name(
    dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE, **kwargs: dict
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan")
    dct = DataCollectingTypeFactory(type=dct_type)
    return ProgramFactory(
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        **kwargs,
    )


def generate_beneficiary_groups() -> None:
    BeneficiaryGroupFactory(
        name="Household",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    BeneficiaryGroupFactory(
        name="Social Workers",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=False,
    )


def generate_people_program() -> None:
    from extras.test_utils.factories.household import (
        create_household,
        create_individual_document,
    )
    from hope.apps.household.models import HOST, SEEING

    ba = BusinessArea.objects.get(name="Afghanistan")
    people_program = ProgramFactory(
        name="Initial_Program_People (sw)",
        status="ACTIVE",
        start_date="2023-06-19",
        end_date="2029-12-24",
        description="qwerty",
        business_area=ba,
        budget="100000.00",
        frequency_of_payments="REGULAR",
        sector="EDUCATION",
        scope="UNICEF",
        cash_plus=False,
        data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
        programme_code="ABC1",
        beneficiary_group=BeneficiaryGroup.objects.get(name="Social Workers"),
        cycle__unicef_id="PC-23-0060-000001",
        cycle__title="Default Program Cycle 1",
        cycle__status="DRAFT",
        cycle__start_date="2023-06-19",
        cycle__end_date="2023-12-24",
    )
    # add one individual
    household, individuals = create_household(
        household_args={
            "business_area": ba,
            "program": people_program,
            "residence_status": HOST,
        },
        individual_args={
            "full_name": "Stacey Freeman",
            "given_name": "Stacey",
            "middle_name": "",
            "family_name": "Freeman",
            "business_area": ba,
            "observed_disability": [SEEING],
        },
    )
    individual = individuals[0]
    create_individual_document(individual)
