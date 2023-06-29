import time
from typing import Any

import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

faker = Faker()


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport

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
    datahub_id = factory.Faker("uuid4")
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> RegistrationDataImport:
        created_at = kwargs.pop("created_at", None)
        obj = super()._create(target_class, *args, **kwargs)
        if created_at:
            obj.created_at = created_at
            obj.save()
        return obj
