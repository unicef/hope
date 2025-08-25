import time
from typing import Any

import factory.fuzzy
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.program import ProgramFactory
from factory.django import DjangoModelFactory
from faker import Faker
from pytz import utc

from models.account import User
from models.core import BusinessArea
from models.program import Program
from models.registration_data import (
    ImportData,
    KoboImportData,
    RegistrationDataImport,
    RegistrationDataImportDatahub,
)

faker = Faker()


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport
        django_get_or_create = ("name",)

    name = factory.LazyFunction(
        lambda: f"{faker.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)} - {time.time_ns()}"
    )
    status = "IN_REVIEW"
    import_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        tzinfo=utc,
    )
    imported_by = factory.SubFactory(UserFactory)
    data_source = factory.fuzzy.FuzzyChoice(
        RegistrationDataImport.DATA_SOURCE_CHOICE,
        getter=lambda c: c[0],
    )
    number_of_individuals = factory.fuzzy.FuzzyInteger(100, 10000)
    number_of_households = factory.fuzzy.FuzzyInteger(3, 50)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    erased = False

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> RegistrationDataImport:
        created_at = kwargs.pop("created_at", None)
        obj = super()._create(target_class, *args, **kwargs)
        if created_at:
            obj.created_at = created_at
            obj.save()
        return obj


class RegistrationDataImportDatahubFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImportDatahub

    factory.LazyFunction(
        lambda: f"{faker.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)} - {time.time_ns()}"
    )
    import_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        tzinfo=utc,
    )


def generate_rdi() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    program = Program.objects.get(name="Initial_Program_People (sw)")
    user_root = User.objects.get(username="root")
    RegistrationDataImportFactory(
        name="Test people merge",
        status="MERGED",
        import_date="2022-03-30 09:22:14.870-00:00",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=7,
        number_of_households=0,
        error_message="",
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        program=program,
    )
    RegistrationDataImportFactory(
        name="test_in_review",
        status="IN_REVIEW",
        import_date="2024-06-04T13:06:23.601Z",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=10,
        number_of_households=0,
        batch_duplicates=0,
        batch_possible_duplicates=0,
        batch_unique=10,
        golden_record_duplicates=0,
        golden_record_possible_duplicates=0,
        golden_record_unique=10,
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        excluded=False,
        program=program,
        erased=False,
        refuse_reason=None,
    )


class ImportDataFactory(DjangoModelFactory):
    class Meta:
        model = ImportData

    status = ImportData.STATUS_FINISHED
    business_area_slug = "afghanistan"
    data_type = ImportData.XLSX
    number_of_households = factory.fuzzy.FuzzyInteger(5, 100)
    number_of_individuals = factory.fuzzy.FuzzyInteger(10, 300)
    error = ""
    validation_errors = ""
    created_by_id = factory.LazyAttribute(lambda o: UserFactory().id)
    file = factory.django.FileField(filename="test_data.xlsx")


class KoboImportDataFactory(DjangoModelFactory):
    class Meta:
        model = KoboImportData

    status = ImportData.STATUS_FINISHED
    business_area_slug = "afghanistan"
    data_type = ImportData.JSON
    number_of_households = factory.fuzzy.FuzzyInteger(5, 100)
    number_of_individuals = factory.fuzzy.FuzzyInteger(10, 300)
    error = ""
    validation_errors = ""
    created_by_id = factory.LazyAttribute(lambda o: UserFactory().id)
    kobo_asset_id = factory.LazyFunction(lambda: f"kobo_{time.time_ns()}")
    only_active_submissions = True
    pull_pictures = True
